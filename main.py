import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Auto Radar Global v2")

DATA_DIR = Path(os.getenv("AUTO_RADAR_DATA_DIR", "data"))
BRIEF_PATH = DATA_DIR / "auto_radar_daily_brief.json"

TWSE_STOCK_DAY_ALL_URL = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
TPEX_MAINBOARD_QUOTES_URL = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
HTTP_TIMEOUT = 8
UP_THRESHOLD_PCT = 0.5

BASE_BRIEF = {
    "date": "2026-06-24",
    "market_mode": "BULL",
    "attack_score": 82,
    "recommended_exposure": 50,
    "main_theme": "AI",
    "top_theme": "散熱水冷",
    "next_theme": "CPO / 矽光子",
    "avoid_theme": "BBU / 伺服器備用電池",
    "risk_event": "美國 CPI D-2",
    "strategy": "可進攻，但因 CPI 事件風險，總持股上限壓制到 50%，禁止追高。",
}

EVENT_OVERLAYS = [
    {
        "event_id": "micron_fy2026_q3_ai_memory_beat",
        "title": "Micron FY2026 Q3 財報優於預期，AI 記憶體供需緊俏",
        "source": "小G Event Intelligence / verified news overlay",
        "confidence": 90,
        "risk_mode": "Risk On",
        "impacts": {
            "記憶體 DRAM/HBM/NAND": 25,
            "AI 基礎設施": 15,
            "CPO / 矽光子": 8,
            "散熱水冷": 6,
            "BBU / 伺服器備用電池": 0,
        },
        "summary": "Micron 財報與展望強化 HBM、DRAM、NAND、AI Server 與高階資料中心需求，事件層對記憶體與 AI 供應鏈給予正向加權。",
    }
]

THEME_BASKETS = [
    {
        "theme": "記憶體 DRAM/HBM/NAND",
        "base_score": 55,
        "stage": "Stage 2",
        "status": "事件催化接棒候選",
        "allocation": 10,
        "entry": "等開盤量能確認，優先觀察強勢股是否鎖定 5 日線上方",
        "take_profit": "+10% 先出一半，+20% 啟動移動停利",
        "stop_loss": "-7%",
        "risk": "事件催化後容易高開震盪，禁止無量追價",
        "leaders": [
            {"symbol": "2408", "name": "南亞科", "market": "TWSE", "weight": 0.35},
            {"symbol": "2344", "name": "華邦電", "market": "TWSE", "weight": 0.35},
            {"symbol": "8299", "name": "群聯", "market": "TPEX", "weight": 0.30},
        ],
    },
    {
        "theme": "散熱水冷",
        "base_score": 84,
        "stage": "Stage 4",
        "status": "法人主升段",
        "allocation": 30,
        "entry": "等回測 5 日線不破，或帶量突破平台",
        "take_profit": "+10% 先出一半，+20% 再出一半",
        "stop_loss": "-7%",
        "risk": "高檔量縮，禁止開高追價",
        "leaders": [
            {"symbol": "3324", "name": "雙鴻", "market": "TPEX", "weight": 0.4},
            {"symbol": "3017", "name": "奇鋐", "market": "TWSE", "weight": 0.4},
            {"symbol": "3653", "name": "健策", "market": "TWSE", "weight": 0.2},
        ],
    },
    {
        "theme": "CPO / 矽光子",
        "base_score": 72,
        "stage": "Stage 2 → 3",
        "status": "接棒候選",
        "allocation": 15,
        "entry": "開盤 15 分鐘量能 > 5 日均量 1.5 倍，且不開高走低",
        "take_profit": "+10% 先出一半，+20% 啟動移動停利",
        "stop_loss": "-7%",
        "risk": "波動高，假突破率高",
        "leaders": [
            {"symbol": "3163", "name": "波若威", "market": "TPEX", "weight": 0.4},
            {"symbol": "3450", "name": "聯鈞", "market": "TWSE", "weight": 0.3},
            {"symbol": "4908", "name": "前鼎", "market": "TPEX", "weight": 0.3},
        ],
    },
    {
        "theme": "BBU / 伺服器備用電池",
        "base_score": 38,
        "stage": "Stage 5",
        "status": "禁止碰",
        "allocation": 0,
        "entry": "不進場",
        "take_profit": "已有部位逢高減碼",
        "stop_loss": "跌破 5 日線先退出",
        "risk": "融資暴增、法人轉賣、當沖率過高",
        "leaders": [
            {"symbol": "3617", "name": "碩天", "market": "TWSE", "weight": 0.4},
            {"symbol": "6121", "name": "新普", "market": "TPEX", "weight": 0.3},
            {"symbol": "3323", "name": "加百裕", "market": "TPEX", "weight": 0.3},
        ],
    },
]

BASE_CONFIDENCE = {
    "rotation_confidence": {"target": "散熱水冷 → CPO / 矽光子", "score": 78, "meaning": "資金有明顯從高檔散熱外溢到 CPO 的跡象"},
    "transition_confidence": {"target": "CPO / 矽光子 Stage 2 → 3", "score": 85, "meaning": "營收與籌碼正在支持題材升級"},
    "risk_confidence": {"target": "BBU Stage 4 → 5", "score": 92, "meaning": "散戶過熱與高檔出貨風險極高"},
}

WATCHLIST = {"market": "^TWII", "themes": THEME_BASKETS}
scheduler = BackgroundScheduler(timezone="Asia/Taipei")
_market_cache: Dict[str, Any] = {}


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str):
            value = value.replace(",", "").replace("+", "").replace("%", "").strip()
            if value in {"", "--", "-", "X", "除權息", "除息", "除權"}:
                return default
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return default
        return number
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    return int(round(safe_float(value, float(default))))


def clamp(value: Any, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(safe_float(value, float(low))))))


def clamp_float(value: Any, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, safe_float(value, low)))


def normalize_symbol(symbol: str) -> str:
    return str(symbol).replace(".TW", "").replace(".TWO", "").strip()


def fallback_snapshot(symbol: str, error: str = "no usable market data", source: str = "fallback") -> Dict[str, Any]:
    return {"symbol": symbol, "close": None, "change_pct": 0, "volume": 0, "avg_volume_5d": 0, "volume_ratio_5d": 0, "source": source, "ok": False, "error": error}


def get_json(url: str, cache_key: str) -> Any:
    if cache_key in _market_cache:
        return _market_cache[cache_key]
    response = requests.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": "AutoRadarGlobal/2.1"})
    response.raise_for_status()
    payload = response.json()
    _market_cache[cache_key] = payload
    return payload


def get_first(row: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def get_fuzzy(row: Dict[str, Any], exact_keys: List[str], contains_keys: List[str], default: Any = None) -> Any:
    value = get_first(row, exact_keys, None)
    if value not in (None, ""):
        return value
    for key, val in row.items():
        key_text = str(key).lower()
        if val not in (None, "") and any(token.lower() in key_text for token in contains_keys):
            return val
    return default


def row_code_matches(row: Dict[str, Any], code: str) -> bool:
    code_keys = ["Code", "code", "證券代號", "有價證券代號", "公司代號", "SecuritiesCompanyCode", "SecuritiesCode", "StockNo", "StockCode", "股票代號", "代號"]
    candidate = str(get_first(row, code_keys, "")).strip()
    if candidate == code:
        return True
    for key, val in row.items():
        key_text = str(key).lower()
        if any(token in key_text for token in ["code", "代號", "stockno", "symbol"]):
            if str(val).strip() == code:
                return True
    return False


def snapshot_from_quote(symbol: str, quote: Dict[str, Any], source: str) -> Dict[str, Any]:
    close = safe_float(get_fuzzy(quote, ["ClosingPrice", "Close", "close", "收盤價", "ClosePrice", "LatestPrice", "最新成交價"], ["closing", "close", "收盤", "最新成交", "latest"]), math.nan)
    change = safe_float(get_fuzzy(quote, ["Change", "ChangePrice", "漲跌價差", "漲跌", "PriceChange", "ChangeAmount", "UpDown"], ["change", "漲跌"]), 0)
    change_pct_from_api = safe_float(get_fuzzy(quote, ["ChangePercent", "漲跌百分比", "漲跌幅", "PercentChange"], ["percent", "百分比", "漲跌幅"]), math.nan)
    volume = safe_int(get_fuzzy(quote, ["TradeVolume", "Volume", "成交股數", "成交股數合計", "TradingShares", "成交量"], ["volume", "成交股", "成交量", "trading"]), 0)
    if math.isnan(close) or close <= 0:
        return fallback_snapshot(symbol, f"invalid official quote keys={list(quote.keys())[:20]}", source)
    prev_close = close - change if change else 0
    calculated_pct = (change / prev_close * 100) if prev_close else 0
    change_pct = change_pct_from_api if not math.isnan(change_pct_from_api) else calculated_pct
    return {"symbol": symbol, "close": round(close, 2), "change_pct": round(safe_float(change_pct), 2), "volume": volume, "avg_volume_5d": 0, "volume_ratio_5d": 1 if volume else 0, "source": source, "ok": True}


def fetch_twse_snapshot(symbol: str) -> Dict[str, Any]:
    code = normalize_symbol(symbol)
    try:
        payload = get_json(TWSE_STOCK_DAY_ALL_URL, "twse_stock_day_all")
        for row in payload:
            if row_code_matches(row, code):
                return snapshot_from_quote(code, row, "twse_openapi")
        sample_keys = list(payload[0].keys())[:20] if payload else []
        return fallback_snapshot(code, f"symbol not found in TWSE sample_keys={sample_keys}", "twse_openapi")
    except Exception as exc:
        return fallback_snapshot(code, str(exc), "twse_openapi")


def fetch_tpex_snapshot(symbol: str) -> Dict[str, Any]:
    code = normalize_symbol(symbol)
    try:
        payload = get_json(TPEX_MAINBOARD_QUOTES_URL, "tpex_mainboard_quotes")
        for row in payload:
            if row_code_matches(row, code):
                return snapshot_from_quote(code, row, "tpex_openapi")
        sample_keys = list(payload[0].keys())[:20] if payload else []
        return fallback_snapshot(code, f"symbol not found in TPEx sample_keys={sample_keys}", "tpex_openapi")
    except Exception as exc:
        return fallback_snapshot(code, str(exc), "tpex_openapi")


def fetch_yfinance_one(yf_symbol: str, original_symbol: str) -> Dict[str, Any]:
    try:
        history = yf.Ticker(yf_symbol).history(period="10d", interval="1d", auto_adjust=False)
        if history.empty or "Close" not in history:
            return fallback_snapshot(original_symbol, f"empty yfinance history for {yf_symbol}", "yfinance")
        close = safe_float(history["Close"].iloc[-1], math.nan)
        prev_close = safe_float(history["Close"].iloc[-2] if len(history) > 1 else close, math.nan)
        volume = safe_float(history["Volume"].iloc[-1] if "Volume" in history else 0, 0)
        avg_volume_5d = safe_float(history["Volume"].tail(5).mean() if "Volume" in history else 0, 0)
        if math.isnan(close) or math.isnan(prev_close) or prev_close == 0:
            return fallback_snapshot(original_symbol, f"invalid yfinance close price for {yf_symbol}", "yfinance")
        change_pct = ((close - prev_close) / prev_close * 100) if prev_close else 0
        volume_ratio = (volume / avg_volume_5d) if avg_volume_5d else 0
        return {"symbol": original_symbol, "close": round(close, 2), "change_pct": round(safe_float(change_pct), 2), "volume": safe_int(volume), "avg_volume_5d": safe_int(avg_volume_5d), "volume_ratio_5d": round(safe_float(volume_ratio), 2), "source": f"yfinance:{yf_symbol}", "ok": True}
    except Exception as exc:
        return fallback_snapshot(original_symbol, str(exc), "yfinance")


def fetch_yfinance_snapshots(symbol: str, market: Optional[str] = None) -> List[Dict[str, Any]]:
    code = normalize_symbol(symbol)
    if not code.isdigit() or "." in symbol:
        return [fetch_yfinance_one(symbol, symbol)]
    preferred = [f"{code}.TWO", f"{code}.TW"] if (market or "").upper() == "TPEX" else [f"{code}.TW", f"{code}.TWO"]
    return [fetch_yfinance_one(yf_symbol, code) for yf_symbol in preferred]


def fetch_symbol_snapshot(symbol: str, market: Optional[str] = None) -> Dict[str, Any]:
    normalized_market = (market or "").upper()
    code = normalize_symbol(symbol)
    attempts: List[Dict[str, Any]] = []
    if code.isdigit():
        if normalized_market == "TWSE":
            attempts.extend([fetch_twse_snapshot(code), fetch_tpex_snapshot(code)])
        elif normalized_market == "TPEX":
            attempts.extend([fetch_tpex_snapshot(code), fetch_twse_snapshot(code)])
        else:
            attempts.extend([fetch_twse_snapshot(code), fetch_tpex_snapshot(code)])
    attempts.extend(fetch_yfinance_snapshots(symbol, normalized_market))
    for result in attempts:
        if result.get("ok"):
            result["attempted_sources"] = [item.get("source") for item in attempts]
            return result
    fallback = fallback_snapshot(symbol, "all data sources failed", "multi_source")
    fallback["attempted_sources"] = [item.get("source") for item in attempts]
    fallback["errors"] = [item.get("error") for item in attempts if item.get("error")]
    return fallback


def sigmoid_score(value: float, slope: float = 0.8, midpoint: float = 0.0) -> int:
    return clamp(100 / (1 + math.exp(-slope * (value - midpoint))))


def normalize_price_score(avg_change_pct: float) -> int:
    return sigmoid_score(avg_change_pct, slope=0.85, midpoint=0.0)


def normalize_volume_score(avg_volume_ratio: float) -> int:
    ratio = max(0.01, safe_float(avg_volume_ratio, 0))
    return clamp(50 + math.log2(ratio) * 50)


def leader_participation_score(change_pct: float) -> float:
    return clamp_float((safe_float(change_pct) + 2) / 4 * 100)


def map_auto_stage(stage_score: float) -> str:
    if stage_score < 20:
        return "Stage 6"
    if stage_score < 40:
        return "Stage 1"
    if stage_score < 55:
        return "Stage 2"
    if stage_score < 70:
        return "Stage 3"
    if stage_score < 85:
        return "Stage 4"
    return "Stage 5"


def map_auto_stage_label(stage_score: float) -> str:
    labels = {
        "Stage 6": "Stage 6 嚴重超賣 / 築底期",
        "Stage 1": "Stage 1 初步復甦 / 懷疑期",
        "Stage 2": "Stage 2 溫和上漲 / 成長期",
        "Stage 3": "Stage 3 主升段 / 熱絡期",
        "Stage 4": "Stage 4 末升段 / 瘋狂期",
        "Stage 5": "Stage 5 高檔震盪 / 出貨反轉期",
    }
    return labels[map_auto_stage(stage_score)]


def stock_momentum_delta(change_pct: float, volume_ratio: float) -> int:
    price_score = normalize_price_score(change_pct)
    volume_score = normalize_volume_score(volume_ratio)
    return int(round(((price_score - 50) * 0.12) + ((volume_score - 50) * 0.08)))


def stage_confidence(data_coverage: float, leader_consistency: float, breadth_score: float) -> int:
    return clamp(data_coverage * 0.4 + leader_consistency * 0.3 + breadth_score * 0.3)


def event_impact_for_theme(theme_name: str) -> Dict[str, Any]:
    score_delta = 0
    stage_delta = 0
    active = []
    for event in EVENT_OVERLAYS:
        impact = safe_float(event.get("impacts", {}).get(theme_name, 0), 0)
        if impact:
            score_delta += impact
            stage_delta += impact * 0.6
            active.append({"title": event["title"], "impact": impact, "confidence": event.get("confidence", 0), "risk_mode": event.get("risk_mode", "")})
    return {"score_delta": round(score_delta, 1), "stage_delta": round(stage_delta, 1), "active_events": active}


def build_theme_from_basket(basket: Dict[str, Any]) -> Dict[str, Any]:
    leaders = []
    weighted_change_sum = 0.0
    weighted_volume_sum = 0.0
    weighted_participation_sum = 0.0
    live_weight_sum = 0.0
    live_deltas = []
    positive_weight = 0.0

    for leader in basket["leaders"]:
        snapshot = fetch_symbol_snapshot(leader["symbol"], leader.get("market"))
        item = dict(leader)
        item["market_data"] = snapshot
        leaders.append(item)
        if snapshot.get("ok"):
            weight = safe_float(leader.get("weight", 1), 1)
            change_pct = safe_float(snapshot.get("change_pct"), 0)
            volume_ratio = safe_float(snapshot.get("volume_ratio_5d"), 0)
            weighted_change_sum += change_pct * weight
            weighted_volume_sum += volume_ratio * weight
            weighted_participation_sum += leader_participation_score(change_pct) * weight
            live_weight_sum += weight
            live_deltas.append(stock_momentum_delta(change_pct, volume_ratio) * weight)
            if change_pct >= UP_THRESHOLD_PCT:
                positive_weight += weight

    total_weight = sum(safe_float(leader.get("weight", 1), 1) for leader in basket["leaders"])
    data_coverage = round((live_weight_sum / total_weight) * 100, 1) if total_weight else 0
    avg_change = weighted_change_sum / live_weight_sum if live_weight_sum else 0
    avg_volume_ratio = weighted_volume_sum / live_weight_sum if live_weight_sum else 0
    avg_delta = sum(live_deltas) / live_weight_sum if live_weight_sum else 0

    overlay = event_impact_for_theme(basket["theme"])
    event_score_delta = safe_float(overlay["score_delta"], 0)
    event_stage_delta = safe_float(overlay["stage_delta"], 0)

    breadth_score = round(weighted_participation_sum / live_weight_sum, 1) if live_weight_sum else 0
    raw_breadth_ratio = round((positive_weight / live_weight_sum) * 100, 1) if live_weight_sum else 0
    price_score = normalize_price_score(avg_change)
    volume_score = normalize_volume_score(avg_volume_ratio)
    base_stage_score = round(price_score * 0.4 + volume_score * 0.3 + breadth_score * 0.3, 1)
    stage_score = round(clamp_float(base_stage_score + event_stage_delta), 1)
    auto_stage = map_auto_stage(stage_score)
    auto_stage_label = map_auto_stage_label(stage_score)

    if not live_weight_sum:
        leader_consistency = 0
    else:
        up_ratio = positive_weight / live_weight_sum
        down_ratio = 1 - up_ratio
        leader_consistency = round(max(up_ratio, down_ratio) * 100, 1)

    confidence = stage_confidence(data_coverage, leader_consistency, breadth_score)

    theme = {
        "theme": basket["theme"],
        "score": clamp(safe_float(basket["base_score"], 0) + avg_delta + event_score_delta),
        "base_score": basket["base_score"],
        "stage": basket["stage"],
        "auto_stage": auto_stage,
        "auto_stage_label": auto_stage_label,
        "stage_score": stage_score,
        "base_stage_score": base_stage_score,
        "stage_confidence": confidence,
        "breadth_score": breadth_score,
        "raw_breadth_ratio": raw_breadth_ratio,
        "price_score": price_score,
        "volume_score": volume_score,
        "event_overlay": overlay,
        "data_coverage": data_coverage,
        "leader_consistency": leader_consistency,
        "status": basket["status"],
        "allocation": basket["allocation"],
        "entry": basket["entry"],
        "take_profit": basket["take_profit"],
        "stop_loss": basket["stop_loss"],
        "risk": basket["risk"],
        "leaders": leaders,
        "theme_strength": clamp(50 + avg_change * 5 + avg_volume_ratio * 5 + event_score_delta * 0.4),
        "theme_momentum": round(avg_change, 2),
        "avg_volume_ratio": round(avg_volume_ratio, 2),
        "live_coverage": round(data_coverage / 100, 2),
        "data_status": "live" if live_weight_sum else "fallback",
    }

    risk_notes = []
    if event_score_delta:
        risk_notes.append(f"Event Overlay: 事件加權 +{event_score_delta}")
    if auto_stage == "Stage 5":
        risk_notes.append("Stage Engine: 自動判定高檔震盪 / 出貨風險")
    if auto_stage == "Stage 6":
        theme["allocation"] = 0
        risk_notes.append("Stage Engine: 自動判定退潮 / 築底，禁止進攻")
    elif str(basket.get("stage", "")).startswith("Stage 5"):
        theme["allocation"] = 0
        risk_notes.append("Pipeline: 原始研究 Stage 5 禁止追逐")
    elif live_weight_sum and avg_volume_ratio < 0.7:
        theme["allocation"] = 0
        risk_notes.append("Pipeline: 題材均量比低於 0.7，啟動風控")
    elif live_weight_sum:
        theme["allocation"] = clamp(theme["allocation"] + max(0, int((avg_delta + event_score_delta * 0.1) // 3)), 0, 50)

    if data_coverage < 50:
        risk_notes.append("Pipeline: 題材資料覆蓋率不足 50%")
    if risk_notes:
        theme["risk"] = f"{theme['risk']}｜{'｜'.join(risk_notes)}"
    return theme


def build_daily_brief() -> Dict[str, Any]:
    _market_cache.clear()
    market_snapshot = fetch_symbol_snapshot(WATCHLIST["market"])
    themes = [build_theme_from_basket(theme) for theme in WATCHLIST["themes"]]

    live_scores = [safe_float(theme.get("score"), 0) for theme in themes if theme.get("data_status") == "live"]
    avg_theme_score = sum(live_scores) / len(live_scores) if live_scores else safe_float(BASE_BRIEF["attack_score"], 82)
    event_bias = max([safe_float(event.get("confidence", 0), 0) for event in EVENT_OVERLAYS] + [0]) * 0.03
    attack_score = clamp(avg_theme_score + safe_float(market_snapshot.get("change_pct"), 0) * 2 + event_bias)
    market_mode = "BULL" if attack_score >= 75 else "NEUTRAL" if attack_score >= 55 else "DEFENSIVE"
    ranked = sorted(themes, key=lambda item: safe_float(item.get("score"), 0), reverse=True)
    avoid_candidates = [item for item in themes if item.get("allocation", 0) == 0 or item.get("auto_stage") in {"Stage 5", "Stage 6"} or "Stage 5" in item.get("stage", "")]
    brief = dict(BASE_BRIEF)
    brief.update({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "market_mode": market_mode,
        "attack_score": attack_score,
        "recommended_exposure": 50 if attack_score >= 75 else 30 if attack_score >= 55 else 10,
        "top_theme": ranked[0]["theme"],
        "next_theme": ranked[1]["theme"] if len(ranked) > 1 else ranked[0]["theme"],
        "avoid_theme": avoid_candidates[0]["theme"] if avoid_candidates else ranked[-1]["theme"],
        "strategy": "Dashboard 已接 Event Overlay v1：小G 事件訊號會轉成 Theme Score 與 Stage Score 加權，但仍由市場資料確認。",
        "data_status": "live" if any(t.get("data_status") == "live" for t in themes) else "fallback",
        "market_snapshot": market_snapshot,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    })
    return {"brief": brief, "themes": themes, "events": EVENT_OVERLAYS, "confidence": BASE_CONFIDENCE, "pipeline": {"version": "Sprint 4.1 Event Overlay v1", "source": "Theme Engine + Stage Engine + Event Intelligence", "fallback": "BASE_BRIEF / THEME_BASKETS / EVENT_OVERLAYS / cached JSON", "schedule": "Asia/Taipei 08:30 daily"}}


def save_daily_brief(payload: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BRIEF_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_daily_brief() -> Dict[str, Any]:
    if BRIEF_PATH.exists():
        try:
            return json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    payload = build_daily_brief()
    save_daily_brief(payload)
    return payload


def run_pipeline() -> Dict[str, Any]:
    payload = build_daily_brief()
    save_daily_brief(payload)
    return payload


@app.on_event("startup")
def startup_event() -> None:
    try:
        run_pipeline()
    except Exception as exc:
        print(f"Pipeline startup fallback: {exc}")
    if not scheduler.running:
        scheduler.add_job(run_pipeline, "cron", hour=8, minute=30, id="daily_pipeline", replace_existing=True)
        scheduler.start()


@app.get("/")
def home():
    return {"project": "Auto Radar Global v2", "status": "running", "routes": ["/healthz", "/brief", "/confidence", "/dashboard", "/pipeline/run", "/data/current", "/debug/market/{symbol}"]}


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/brief")
def brief():
    payload = load_daily_brief()
    return {"brief": payload["brief"], "themes": payload["themes"], "pipeline": payload.get("pipeline", {})}


@app.get("/confidence")
def confidence():
    return load_daily_brief().get("confidence", BASE_CONFIDENCE)


@app.get("/data/current")
def data_current():
    return load_daily_brief()


@app.get("/debug/market/{symbol}")
def debug_market(symbol: str, market: Optional[str] = None):
    _market_cache.clear()
    return fetch_symbol_snapshot(symbol, market)


@app.post("/pipeline/run")
def pipeline_run():
    return run_pipeline()


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    payload = load_daily_brief()
    brief_data = payload["brief"]
    themes = payload["themes"]
    confidence_data = payload.get("confidence", BASE_CONFIDENCE)
    events = payload.get("events", [])
    event_html = ""
    for event in events:
        impacts = "、".join([f"{k} +{v}" for k, v in event.get("impacts", {}).items() if safe_float(v, 0)])
        event_html += f"<p><b>{event.get('title')}</b><br>Risk：{event.get('risk_mode')}｜Confidence：{event.get('confidence')}｜Impact：{impacts}</p>"

    theme_cards = ""
    for t in themes:
        leaders_html = ""
        for leader in t.get("leaders", []):
            md = leader.get("market_data", {})
            weight = int(safe_float(leader.get("weight", 0), 0) * 100)
            if md.get("ok"):
                leader_line = f"{leader.get('symbol')} {leader.get('name')}｜權重 {weight}%｜{md.get('source')}｜{md.get('change_pct')}%｜量比 {md.get('volume_ratio_5d')}x"
            else:
                leader_line = f"{leader.get('symbol')} {leader.get('name')}｜權重 {weight}%｜fallback｜{md.get('error', '')}"
            leaders_html += f"<li>{leader_line}</li>"
        overlay = t.get("event_overlay", {})
        overlay_line = f"事件加權：Score +{overlay.get('score_delta', 0)}｜Stage +{overlay.get('stage_delta', 0)}" if overlay.get("score_delta") else "事件加權：無"
        theme_cards += f"""
        <div class="card">
            <h2>{t['theme']}</h2>
            <p><b>分數：</b>{t['score']} / 100｜<b>基準：</b>{t.get('base_score')}</p>
            <p><b>題材強度：</b>{t.get('theme_strength')}｜<b>題材動能：</b>{t.get('theme_momentum')}%｜<b>覆蓋率：</b>{int(t.get('live_coverage', 0) * 100)}%</p>
            <p><b>Breadth：</b>{t.get('breadth_score')}｜<b>Raw Up：</b>{t.get('raw_breadth_ratio')}｜<b>Price：</b>{t.get('price_score')}｜<b>Volume：</b>{t.get('volume_score')}</p>
            <p><b>Stage Score：</b>{t.get('stage_score')}｜<b>Base Stage：</b>{t.get('base_stage_score')}｜<b>Auto Stage：</b>{t.get('auto_stage_label')}</p>
            <p><b>Confidence：</b>{t.get('stage_confidence')}｜<b>{overlay_line}</b></p>
            <p><b>原始階段：</b>{t['stage']}｜{t['status']}</p>
            <p><b>建議配置：</b>{t['allocation']}%</p>
            <p><b>Leaders：</b></p><ul>{leaders_html}</ul>
            <p><b>進場條件：</b>{t['entry']}</p>
            <p><b>停利：</b>{t['take_profit']}</p>
            <p><b>停損：</b>{t['stop_loss']}</p>
            <p><b>風險：</b>{t['risk']}</p>
        </div>
        """
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <title>Auto Radar Global v2</title>
        <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
        <style>
            body {{ font-family: Arial, "Microsoft JhengHei", sans-serif; background: #f5f5f5; margin: 0; padding: 24px; color: #111; }}
            .container {{ max-width: 960px; margin: auto; }}
            .hero {{ background: #111; color: white; border-radius: 18px; padding: 24px; margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 16px; }}
            .card {{ background: white; border-radius: 16px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            .tag {{ display: inline-block; color: #ffffff; padding: 7px 12px; border-radius: 999px; margin-right: 8px; font-weight: bold; }}
            .tag.green {{ background: #16a34a; }} .tag.blue {{ background: #2563eb; }} .tag.orange {{ background: #f59e0b; }}
            .warn {{ background: #fff3cd; color: #92400e; font-weight: 800; padding: 14px; border-radius: 12px; margin-top: 12px; }}
            .meta {{ opacity: .8; font-size: 14px; }} h1, h2 {{ margin-top: 0; }}
            ul {{ padding-left: 18px; }} li {{ margin-bottom: 5px; }}
            .actions {{ margin: 18px 0; display: flex; gap: 10px; }}
            button {{ border: 0; border-radius: 999px; padding: 10px 14px; font-weight: 800; cursor: pointer; background: #111; color: white; }}
        </style>
    </head>
    <body>
        <div class="container" id="radar-capture">
            <div class="hero">
                <h1>Auto Radar Daily</h1>
                <p>日期：{brief_data['date']}｜更新：{brief_data.get('updated_at', 'N/A')}</p>
                <p class="meta">Pipeline：{payload.get('pipeline', {}).get('version', 'N/A')}｜資料狀態：{brief_data.get('data_status', 'fallback')}</p>
                <p><span class="tag green">市場模式：{brief_data['market_mode']}</span><span class="tag blue">進攻指數：{brief_data['attack_score']}/100</span><span class="tag orange">建議持股：{brief_data['recommended_exposure']}%</span></p>
                <p><b>主線：</b>{brief_data['main_theme']}</p><p><b>目前主題：</b>{brief_data['top_theme']}</p><p><b>下一個接棒：</b>{brief_data['next_theme']}</p><p><b>禁止碰：</b>{brief_data['avoid_theme']}</p>
                <div class="warn"><b>風險事件：</b>{brief_data['risk_event']}｜{brief_data['strategy']}</div>
            </div>
            <div class="card" style="margin-bottom:20px;"><h2>Overnight Event Overlay</h2>{event_html}</div>
            <div class="grid">{theme_cards}</div>
            <div class="card" style="margin-top:20px;"><h2>小G 信心分數</h2><p><b>輪動信心：</b>{confidence_data['rotation_confidence']['score']}%｜{confidence_data['rotation_confidence']['target']}</p><p><b>升級信心：</b>{confidence_data['transition_confidence']['score']}%｜{confidence_data['transition_confidence']['target']}</p><p><b>風險信心：</b>{confidence_data['risk_confidence']['score']}%｜{confidence_data['risk_confidence']['target']}</p></div>
        </div>
        <div class="container actions"><button onclick="downloadShot()">📥 下載截圖</button><button onclick="copyShot()">📸 複製截圖</button></div>
        <script>
            async function makeCanvas() {{ return await html2canvas(document.getElementById('radar-capture'), {{backgroundColor: '#f5f5f5', scale: 2}}); }}
            async function downloadShot() {{ const canvas = await makeCanvas(); const a = document.createElement('a'); a.download = 'auto-radar-daily.png'; a.href = canvas.toDataURL('image/png'); a.click(); }}
            async function copyShot() {{ const canvas = await makeCanvas(); canvas.toBlob(async blob => {{ await navigator.clipboard.write([new ClipboardItem({{'image/png': blob}})]); alert('已複製截圖'); }}); }}
        </script>
    </body>
    </html>
    """
    return html
