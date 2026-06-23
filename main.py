from fastapi import FastAPI

app = FastAPI(title="Auto Radar Global v2")


@app.get("/")
def home():
    return {
        "project": "Auto Radar Global v2",
        "status": "running"
    }


@app.get("/healthz")
def healthz():
    return {
        "ok": True
    }
