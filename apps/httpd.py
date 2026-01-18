from fastapi import FastAPI
from fastapi.responses import JSONResponse
import ipc

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def api_status():
    print("GET /api/status")
    try:
        r = ipc.request("get_status", timeout=0.5)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            print("IPC outcome: error")
            code = r.get("error", {}).get("code", "unknown_error")
            return JSONResponse(status_code=503, content={"error": "ipc_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_error", "details": str(e)})

@app.get("/api/metrics")
def api_metrics():
    print("GET /api/metrics")
    try:
        r = ipc.request("get_metrics", timeout=0.5)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            print("IPC outcome: error")
            code = r.get("error", {}).get("code", "unknown_error")
            return JSONResponse(status_code=503, content={"error": "ipc_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_error", "details": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
