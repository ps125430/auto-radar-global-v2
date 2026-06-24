import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Auto Radar Global v2")

DATA_DIR = Path(os.getenv("AUTO_RADAR_DATA_DIR", "data"))
BRIEF_PATH = DATA_DIR / "auto_radar_daily_brief.json"

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

BASE_THEMES = [
    {
        "theme": "散熱水冷",
        "score": 84,
        "stage": "Stage 4",
        "status": "法人主升段",
        "allocation": 30,
        "entry": "等回測 5 日線不破，或帶量突破平台",
        "take_profit": "+10% 先出一半，+20% 再出一半",
        "stop_loss": "-7%",
        "risk": "高檔量縮，禁止開高追價",
        "symbol": "3324.TW",
    },
    {
        "theme": "CPO / 矽光子",
        "score": 72,
        "stage": "Stage 2 → 3",
        "status": "接棒候選",
        "allocation": 15,
        "entry": "開盤 15 分鐘量能 > 5 日均量 1.5 倍，且不開高走低",
        "take_profit": "+10% 先出一半，+20% 啟動移動停利",
        "stop_loss": "-7%",
        "risk": "波動高，假突破率高",
        "symbol": "3163.TWO",
    },
    {
        "theme": "BBU / 伺服器備用電池",
        "score": 38,
        "stage": "Stage 5",
        "status": "禁止碰",
        "allocation": 0,
        "entry": "不進場",
        "take_profit": "已有部位逢高減碼",
        "stop_loss": "跌破 5 日線先退出",
        "risk": "融資暴增、法人轉賣、當沖率過高",
        "symbol": "3617.TW",
    },
]

BASE_CONFIDENCE = {
    "rotation_confidence": {
        "target": "散熱水冷 → CPO / 矽光子",
        "score": 78,
        "meaning": "資金有明顯從高檔散熱外溢到 CPO 的跡象",
    },
    "transition_confidence": {
        "target": "CPO / 矽光子 Stage 2 → 3",
        "score": 85,
        "meaning": "營收與籌碼正在支持題材升級",
    },
    "risk_confidence": {
        "target": "BBU Stage 4 → 5",
        "score": 92,
        "meaning": "散戶過熱與高檔出貨風險極高",
    },
}

WATCHLIST = {
    "market": "^TWII",
    "themes": BASE_THEMES,
}

scheduler = BackgroundScheduler(timezone="Asia/Taipei")


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def fetch_symbol_snapshot(symbol: str) -> Dict[str, Any]:
    """Fetch a compact daily market snapshot. The pipeline fails soft on free infra."""
    try:
        history = yf.Ticker(symbol).history(period="10d", interval="1d", auto_adjust=False)
        if history.empty:
            raise ValueError("empty history")

        close = float(history["Close"].iloc[-1])
        prev_close = float(history["Close"].iloc[-2]) if len(history) > 1 else close
        volume = float(history["Volume"].iloc[-1]) if "Volume" in history else 0
        avg_volume_5d = float(history["Volume"].tail(5).mean()) if "Volume" in history else 0
        change_pct = ((close - prev_close) / prev_close * 100) if prev_close else 0
        volume_ratio = (volume / avg_volume_5d) if avg_volume_5d else 0

        return {
            "symbol": symbol,
            "close": round(close, 2),
            "change_pct": round(change_pct, 2),
            "volume": int(volume),
            "avg_volume_5d": int(avg_volume_5d),
            "volume_ratio_5d": round(volume_ratio, 2),
            "source": "yfinance",
            "ok": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "symbol": symbol,
            "close": None,
            "change_pct": 0,
            "volume": 0,
            "avg_volume_5d": 0,
            "volume_ratio_5d": 0,
            "source": "fallback",
            "ok": False,
            "error": str(exc),
        }


def score_theme(base_theme: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Apply Sprint 3 pipeline adjustment without changing 小G's research stage definitions."""
    theme = dict(base_theme)
    theme["market_data"] = snapshot

    if not snapshot.get("ok"):
        theme["data_status"] = "fallback"
        return theme

    change_pct = float(snapshot.get("change_pct") or 0)
    volume_ratio = float(snapshot.get("volume_ratio_5d") or 0)

    momentum_delta = 0
    if change_pct >= 3:
        momentum_delta += 6
    elif change_pct >= 1:
        momentum_delta += 3
    elif change_pct <= -3:
        momentum_delta -= 8
    elif change_pct <= -1:
        momentum_delta -= 4

    volume_delta = 0
    if volume_ratio >= 1.5:
        volume_delta += 5
    elif volume_ratio >= 1.1:
        volume_delta += 2
    elif 0 < volume_ratio < 0.7:
        volume_delta -= 8

    stage = str(theme.get("stage", ""))
    risk_notes = []
    if stage.startswith("Stage 5"):
        theme["allocation"] = 0
        risk_notes.append("Pipeline: Stage 5 禁止追逐")
    elif stage.startswith("Stage 6") or (0 < volume_ratio < 0.7):
        theme["allocation"] = 0
        risk_notes.append("Pipeline: 量能低於 5 日均量 0.7 倍，啟動風控")
    else:
        theme["allocation"] = clamp(theme["allocation"] + max(0, momentum_delta // 2), 0, 50)

    if risk_notes:
        theme["risk"] = f"{theme['risk']}｜{'｜'.join(risk_notes)}"

    theme["score"] = clamp(theme["score"] + momentum_delta + volume_delta)
    theme["data_status"] = "live"
    return theme


def build_daily_brief() -> Dict[str, Any]:
    market_snapshot = fetch_symbol_snapshot(WATCHLIST["market"])
    themes = [score_theme(theme, fetch_symbol_snapshot(theme["symbol"])) for theme in WATCHLIST["themes"]]

    live_scores = [theme["score"] for theme in themes if theme.get("data_status") == "live"]
    avg_theme_score = sum(live_scores) / len(live_scores) if live_scores else BASE_BRIEF["attack_score"]
    market_change = float(market_snapshot.get("change_pct") or 0)
    attack_score = clamp(avg_theme_score + market_change * 2)

    if attack_score >= 75:
        market_mode = "BULL"
    elif attack_score >= 55:
        market_mode = "NEUTRAL"
    else:
        market_mode = "DEFENSIVE"

    ranked = sorted(themes, key=lambda item: item["score"], reverse=True)
    avoid_candidates = [
        item for item in themes
        if item.get("allocation", 0) == 0 or "Stage 5" in item.get("stage", "") or "Stage 6" in item.get("stage", "")
    ]

    brief = dict(BASE_BRIEF)
    brief.update(
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market_mode": market_mode,
            "attack_score": attack_score,
            "recommended_exposure": 50 if attack_score >= 75 else 30 if attack_score >= 55 else 10,
            "top_theme": ranked[0]["theme"],
            "next_theme": ranked[1]["theme"] if len(ranked) > 1 else ranked[0]["theme"],
            "avoid_theme": avoid_candidates[0]["theme"] if avoid_candidates else ranked[-1]["theme"],
            "strategy": "Dashboard 已接 Pipeline v1：以每日市場資料更新分數與持股上限；Stage 5 / Stage 6 / 量能跌破門檻仍優先風控。",
            "data_status": "live" if any(t.get("data_status") == "live" for t in themes) else "fallback",
            "market_snapshot": market_snapshot,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
    )

    return {
        "brief": brief,
        "themes": themes,
        "confidence": BASE_CONFIDENCE,
        "pipeline": {
            "version": "Sprint 3 Data Pipeline v1",
            "source": "yfinance",
            "fallback": "BASE_BRIEF / BASE_THEMES / BASE_CONFIDENCE",
            "schedule": "Asia/Taipei 08:30 daily",
        },
    }


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
    run_pipeline()
    if not scheduler.running:
        scheduler.add_job(run_pipeline, "cron", hour=8, minute=30, id="daily_pipeline", replace_existing=True)
        scheduler.start()


@app.get("/")
def home():
    return {
        "project": "Auto Radar Global v2",
        "status": "running",
        "routes": ["/healthz", "/brief", "/confidence", "/dashboard", "/pipeline/run", "/data/current"],
    }


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


@app.post("/pipeline/run")
def pipeline_run():
    return run_pipeline()


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    payload = load_daily_brief()
    brief_data = payload["brief"]
    themes = payload["themes"]
    confidence_data = payload.get("confidence", BASE_CONFIDENCE)

    theme_cards = ""
    for t in themes:
        md = t.get("market_data", {})
        market_line = "資料來源：fallback"
        if md.get("ok"):
            market_line = (
                f"收盤：{md.get('close')}｜漲跌：{md.get('change_pct')}%｜"
                f"量比：{md.get('volume_ratio_5d')}x"
            )

        theme_cards += f"""
        <div class="card">
            <h2>{t['theme']}</h2>
            <p><b>分數：</b>{t['score']} / 100</p>
            <p><b>階段：</b>{t['stage']}｜{t['status']}</p>
            <p><b>建議配置：</b>{t['allocation']}%</p>
            <p><b>Pipeline：</b>{market_line}</p>
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
        <style>
            body {{
                font-family: Arial, "Microsoft JhengHei", sans-serif;
                background: #f5f5f5;
                margin: 0;
                padding: 24px;
                color: #111;
            }}
            .container {{ max-width: 960px; margin: auto; }}
            .hero {{ background: #111; color: white; border-radius: 18px; padding: 24px; margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
            .card {{ background: white; border-radius: 16px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            .tag {{ display: inline-block; color: #ffffff; padding: 7px 12px; border-radius: 999px; margin-right: 8px; font-weight: bold; }}
            .tag.green {{ background: #16a34a; }}
            .tag.blue {{ background: #2563eb; }}
            .tag.orange {{ background: #f59e0b; }}
            .warn {{ background: #fff3cd; color: #92400e; font-weight: 800; padding: 14px; border-radius: 12px; margin-top: 12px; }}
            .meta {{ opacity: .8; font-size: 14px; }}
            h1, h2 {{ margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>Auto Radar Daily</h1>
                <p>日期：{brief_data['date']}｜更新：{brief_data.get('updated_at', 'N/A')}</p>
                <p class="meta">Pipeline：{payload.get('pipeline', {}).get('version', 'N/A')}｜資料狀態：{brief_data.get('data_status', 'fallback')}</p>
                <p>
                    <span class="tag green">市場模式：{brief_data['market_mode']}</span>
                    <span class="tag blue">進攻指數：{brief_data['attack_score']}/100</span>
                    <span class="tag orange">建議持股：{brief_data['recommended_exposure']}%</span>
                </p>
                <p><b>主線：</b>{brief_data['main_theme']}</p>
                <p><b>目前主題：</b>{brief_data['top_theme']}</p>
                <p><b>下一個接棒：</b>{brief_data['next_theme']}</p>
                <p><b>禁止碰：</b>{brief_data['avoid_theme']}</p>
                <div class="warn"><b>風險事件：</b>{brief_data['risk_event']}｜{brief_data['strategy']}</div>
            </div>

            <div class="grid">
                {theme_cards}
            </div>

            <div class="card" style="margin-top:20px;">
                <h2>小G 信心分數</h2>
                <p><b>輪動信心：</b>{confidence_data['rotation_confidence']['score']}%｜{confidence_data['rotation_confidence']['target']}</p>
                <p><b>升級信心：</b>{confidence_data['transition_confidence']['score']}%｜{confidence_data['transition_confidence']['target']}</p>
                <p><b>風險信心：</b>{confidence_data['risk_confidence']['score']}%｜{confidence_data['risk_confidence']['target']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
