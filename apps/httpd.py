from fastapi import FastAPI
from fastapi.responses import JSONResponse
import ipc

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def api_status():
    try:
        r = ipc.request("get_status", timeout=0.5)
        if r.get("ok"):
            return r["result"]
    except Exception:
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})
    return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

@app.get("/api/metrics")
def api_metrics():
    try:
        r = ipc.request("get_metrics", timeout=0.5)
        if r.get("ok"):
            return r["result"]
    except Exception:
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})
    return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
