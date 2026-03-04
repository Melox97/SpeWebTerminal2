from fastapi import FastAPI
from fastapi.responses import JSONResponse
import ipc
import shutil
import os
from datetime import datetime
from apps.config import IPC_CALL_TIMEOUT_S_DEFAULT

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/get_log")
def debug_get_log():
    log_dir = os.path.join(os.getcwd(), "log")
    runtime_log = os.path.join(log_dir, "runtime.log")
    if not os.path.exists(runtime_log):
        return JSONResponse(status_code=409, content={"error": "log_unavailable"})
    
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_name = f"snapshot-{ts}.log"
    snapshot_path = os.path.join(log_dir, snapshot_name)
    
    try:
        shutil.copy(runtime_log, snapshot_path)
        # Return relative path for clarity
        return {"saved": True, "path": f"log/{snapshot_name}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "copy_failed", "details": str(e)})

@app.get("/api/status")
def api_status():
    print("GET /api/status")
    try:
        r = ipc.request("get_status", timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=503, content={"error": "ipc_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_error", "details": str(e)})

@app.get("/api/metrics")
def api_metrics():
    print("GET /api/metrics")
    try:
        r = ipc.request("get_metrics", timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=503, content={"error": "ipc_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_error", "details": str(e)})

@app.post("/api/probe")
def api_probe():
    print("POST /api/probe")
    try:
        r = ipc.request("serial_probe", timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            # Probe is special, keep minimal log or consistent? 
            # User request: "In apps/httpd.py, quando la chiamata IPC va a buon fine ma la risposta è ok=false ... Logga come..."
            # Probe log was implicit/missing in original code (only print "POST ..."). 
            # But let's add it for consistency if it helps debugging, or leave as is if not requested?
            # The prompt implies fixing where "IPC outcome: error" WAS logged.
            # In api_probe original code, there was NO "IPC outcome: error" print.
            # So I should strictly follow instructions: "Fix logging outcome... quando la chiamata IPC va a buon fine ma la risposta è ok=false ... NON loggare come 'IPC outcome: error'."
            # Since api_probe didn't log that, I leave it alone or just add the print?
            # Let's add the print for consistency with the rule "Logga come...", assuming the user wants visibility.
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=409, content={"error": "serial_error", "details": code})
    except Exception:
        # Original code didn't print error here either
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

@app.post("/api/serial/open")
def api_serial_open():
    print("POST /api/serial/open")
    try:
        r = ipc.request("serial_open", timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=409, content={"error": "serial_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

@app.post("/api/serial/close")
def api_serial_close():
    print("POST /api/serial/close")
    try:
        r = ipc.request("serial_close", timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=409, content={"error": "serial_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

@app.get("/api/serial/recent")
def api_serial_recent(n: int = 50):
    print(f"GET /api/serial/recent?n={n}")
    try:
        r = ipc.request("serial_recent", params={"n": n}, timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=503, content={"error": "ipc_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

@app.post("/api/serial/write")
def api_serial_write(payload: dict):
    print("POST /api/serial/write")
    try:
        data = payload.get("data", "")
        r = ipc.request("serial_write", params={"data": data}, timeout=IPC_CALL_TIMEOUT_S_DEFAULT)
        if r.get("ok"):
            print("IPC outcome: ok")
            return r["result"]
        else:
            code = r.get("error", {}).get("code", "unknown_error")
            print(f"IPC outcome: ok (app_error={code})")
            return JSONResponse(status_code=409, content={"error": "serial_error", "details": code})
    except Exception as e:
        print(f"IPC outcome: error ({str(e)})")
        return JSONResponse(status_code=503, content={"error": "ipc_unavailable"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
