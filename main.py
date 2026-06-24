from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Auto Radar Global v2")


BRIEF = {
    "date": "2026-06-24",
    "market_mode": "BULL",
    "attack_score": 82,
    "recommended_exposure": 50,
    "main_theme": "AI",
    "top_theme": "散熱水冷",
    "next_theme": "CPO / 矽光子",
    "avoid_theme": "BBU / 伺服器備用電池",
    "risk_event": "美國 CPI D-2",
    "strategy": "可進攻，但因 CPI 事件風險，總持股上限壓制到 50%，禁止追高。"
}

THEMES = [
    {
        "theme": "散熱水冷",
        "score": 84,
        "stage": "Stage 4",
        "status": "法人主升段",
        "allocation": 30,
        "entry": "等回測 5 日線不破，或帶量突破平台",
        "take_profit": "+10% 先出一半，+20% 再出一半",
        "stop_loss": "-7%",
        "risk": "高檔量縮，禁止開高追價"
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
        "risk": "波動高，假突破率高"
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
        "risk": "融資暴增、法人轉賣、當沖率過高"
    }
]

CONFIDENCE = {
    "rotation_confidence": {
        "target": "散熱水冷 → CPO / 矽光子",
        "score": 78,
        "meaning": "資金有明顯從高檔散熱外溢到 CPO 的跡象"
    },
    "transition_confidence": {
        "target": "CPO / 矽光子 Stage 2 → 3",
        "score": 85,
        "meaning": "營收與籌碼正在支持題材升級"
    },
    "risk_confidence": {
        "target": "BBU Stage 4 → 5",
        "score": 92,
        "meaning": "散戶過熱與高檔出貨風險極高"
    }
}


@app.get("/")
def home():
    return {
        "project": "Auto Radar Global v2",
        "status": "running",
        "routes": ["/healthz", "/brief", "/confidence", "/dashboard"]
    }


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/brief")
def brief():
    return {
        "brief": BRIEF,
        "themes": THEMES
    }


@app.get("/confidence")
def confidence():
    return CONFIDENCE


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    theme_cards = ""
    for t in THEMES:
        theme_cards += f"""
        <div class="card">
            <h2>{t['theme']}</h2>
            <p><b>分數：</b>{t['score']} / 100</p>
            <p><b>階段：</b>{t['stage']}｜{t['status']}</p>
            <p><b>建議配置：</b>{t['allocation']}%</p>
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
            .container {{
                max-width: 960px;
                margin: auto;
            }}
            .hero {{
                background: #111;
                color: white;
                border-radius: 18px;
                padding: 24px;
                margin-bottom: 20px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 16px;
            }}
            .card {{
                background: white;
                border-radius: 16px;
                padding: 18px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}
           .tag {{
    display: inline-block;
    color: #ffffff;
    padding: 7px 12px;
    border-radius: 999px;
    margin-right: 8px;
    font-weight: bold;
}}

.tag.green {{
    background: #16a34a;
}}

.tag.blue {{
    background: #2563eb;
}}

.tag.orange {{
    background: #f59e0b;
}}

.warn {{
    background: #fff3cd;
    color: #92400e;
    font-weight: 800;
    padding: 14px;
    border-radius: 12px;
    margin-top: 12px;
}}
            h1, h2 {{
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>Auto Radar Daily</h1>
                <p>日期：{BRIEF['date']}</p>
                <p>
                    <span class="tag green">市場模式：{BRIEF['market_mode']}</span>
<span class="tag blue">進攻指數：{BRIEF['attack_score']}/100</span>
<span class="tag orange">建議持股：{BRIEF['recommended_exposure']}%</span>
                </p>
                <p><b>主線：</b>{BRIEF['main_theme']}</p>
                <p><b>目前主題：</b>{BRIEF['top_theme']}</p>
                <p><b>下一個接棒：</b>{BRIEF['next_theme']}</p>
                <p><b>禁止碰：</b>{BRIEF['avoid_theme']}</p>
                <div class="warn"><b>風險事件：</b>{BRIEF['risk_event']}｜{BRIEF['strategy']}</div>
            </div>

            <div class="grid">
                {theme_cards}
            </div>

            <div class="card" style="margin-top:20px;">
                <h2>小G 信心分數</h2>
                <p><b>輪動信心：</b>{CONFIDENCE['rotation_confidence']['score']}%｜{CONFIDENCE['rotation_confidence']['target']}</p>
                <p><b>升級信心：</b>{CONFIDENCE['transition_confidence']['score']}%｜{CONFIDENCE['transition_confidence']['target']}</p>
                <p><b>風險信心：</b>{CONFIDENCE['risk_confidence']['score']}%｜{CONFIDENCE['risk_confidence']['target']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
