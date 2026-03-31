"""
N.E.M.E.S.I.S API Server
FastAPI backend with REST endpoints, WebSocket streaming, and simulation engine integration.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import time

from simulation.engine import SimulationEngine
from simulation.event_bus import event_bus, STATE_MONITORING, STATE_ALERT, STATE_DEFENSE, STATE_LOCKDOWN
from api.ws_manager import ws_manager

app = FastAPI(
    title="N.E.M.E.S.I.S",
    description="Neural Edge-based Mimicry & Entrapment System for IoT Security",
    version="4.2.0",
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation engine
sim_engine: Optional[SimulationEngine] = None


# ─── REQUEST MODELS ──────────────────────────────────────────────────────

class IsolateRequest(BaseModel):
    mac: str
    policy: str = "full_isolation"

class HoneypotRequest(BaseModel):
    target_ip: str
    pot_type: str = "generic"

class StateChangeRequest(BaseModel):
    state: str

class SpeedChangeRequest(BaseModel):
    mode: Optional[str] = None
    custom_value: Optional[float] = None


# ─── LIFECYCLE ───────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Initialize and start the simulation engine."""
    global sim_engine
    print("=" * 60)
    print("  N.E.M.E.S.I.S v4.2 — SYSTEM INITIALIZING")
    print("=" * 60)
    sim_engine = SimulationEngine(speed_mode="demo")
    await sim_engine.start()
    print("[✓] Simulation engine started in DEMO mode")
    print("[✓] Event bus active")
    print("[✓] All agents online")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown():
    """Stop the simulation engine."""
    global sim_engine
    if sim_engine:
        sim_engine.stop()
    print("[✓] N.E.M.E.S.I.S shutdown complete")


# ─── ROOT ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "system": "N.E.M.E.S.I.S",
        "version": "4.2.0",
        "codename": "Neural Edge-based Mimicry & Entrapment System for IoT Security",
        "status": "OPERATIONAL",
        "timestamp": time.time(),
    }


# ─── DEVICE ENDPOINTS ───────────────────────────────────────────────────

@app.get("/devices")
async def get_devices():
    """Get all discovered devices."""
    devices = sim_engine.get_all_devices()
    return {
        "devices": devices,
        "count": len(devices),
        "timestamp": time.time(),
    }


@app.get("/devices/{mac}")
async def get_device(mac: str):
    """Get a specific device by MAC address."""
    device = sim_engine.get_device(mac)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"device": device}


# ─── ALERT ENDPOINTS ────────────────────────────────────────────────────

@app.get("/alerts")
async def get_alerts(limit: int = Query(50, ge=1, le=500)):
    """Get recent alerts from event history."""
    from simulation.event_bus import EVENT_ALERT_CREATED
    alerts = event_bus.get_history(EVENT_ALERT_CREATED, limit=limit)
    return {"alerts": alerts, "count": len(alerts)}


# ─── NETWORK MAP ─────────────────────────────────────────────────────────

@app.get("/network-map")
async def get_network_map():
    """Get current network topology."""
    from simulation.event_bus import EVENT_NETWORK_MAP_UPDATE
    maps = event_bus.get_history(EVENT_NETWORK_MAP_UPDATE, limit=1)
    if maps:
        return maps[-1]["payload"]
    return {"devices": [], "connections": []}


# ─── LOG ENDPOINTS ───────────────────────────────────────────────────────

@app.get("/logs")
async def get_logs(limit: int = Query(100, ge=1, le=1000)):
    """Get recent system logs."""
    from simulation.event_bus import EVENT_LOG_ENTRY
    logs = event_bus.get_history(EVENT_LOG_ENTRY, limit=limit)
    return {"logs": logs, "count": len(logs)}


# ─── THREAT ENDPOINTS ───────────────────────────────────────────────────

@app.get("/threats")
async def get_threats():
    """Get active and historical threats."""
    active = sim_engine.attack_simulator.get_active_attacks()
    history = sim_engine.attack_simulator.get_attack_history(limit=50)
    return {
        "active": active,
        "history": history,
        "active_count": len(active),
        "total_count": len(history),
    }


# ─── HONEYPOT ENDPOINTS ─────────────────────────────────────────────────

@app.get("/honeypots")
async def get_honeypots():
    """Get all honeypots."""
    honeypots = list(sim_engine.agent_beta.honeypots.values())
    return {
        "honeypots": honeypots,
        "active": len([h for h in honeypots if h["status"] == "active"]),
        "total": len(honeypots),
    }


# ─── AGENT STATUS ───────────────────────────────────────────────────────

@app.get("/agents/status")
async def get_agent_status():
    """Get status of all three agents."""
    return {
        "alpha": sim_engine.agent_alpha.get_status(),
        "beta": sim_engine.agent_beta.get_status(),
        "gamma": sim_engine.agent_gamma.get_status(),
    }


# ─── METRICS ─────────────────────────────────────────────────────────────

@app.get("/metrics")
async def get_metrics():
    """Get latest system metrics."""
    from simulation.event_bus import EVENT_METRIC_UPDATE
    metrics = event_bus.get_history(EVENT_METRIC_UPDATE, limit=1)
    if metrics:
        return metrics[-1]["payload"]
    return {}


# ─── SYSTEM STATUS ───────────────────────────────────────────────────────

@app.get("/status")
async def get_status():
    """Get comprehensive system status."""
    return sim_engine.get_full_status()


# ─── COMMAND ENDPOINTS (USER-TRIGGERED ACTIONS) ─────────────────────────

@app.post("/command/isolate")
async def cmd_isolate(req: IsolateRequest):
    """Isolate a device by MAC address."""
    result = await sim_engine.command_isolate(req.mac)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    return result


@app.post("/command/release")
async def cmd_release(req: IsolateRequest):
    """Release a device from isolation."""
    result = await sim_engine.command_release(req.mac)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    return result


@app.post("/command/honeypot")
async def cmd_honeypot(req: HoneypotRequest):
    """Deploy a honeypot."""
    result = await sim_engine.command_deploy_honeypot(req.target_ip, req.pot_type)
    return result


@app.post("/command/state")
async def cmd_state(req: StateChangeRequest):
    """Change system operational state."""
    result = await sim_engine.command_set_state(req.state)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    return result


@app.post("/command/speed")
async def cmd_speed(req: SpeedChangeRequest):
    """Change simulation speed."""
    sim_engine.set_speed(mode=req.mode, custom_value=req.custom_value)
    return {
        "success": True,
        "speed_mode": sim_engine.speed_mode,
        "speed_multiplier": sim_engine.speed_multiplier,
    }


# ─── WEBSOCKET ───────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    await ws_manager.connect(websocket)

    try:
        # Send initial state snapshot
        await ws_manager.send_personal(websocket, {
            "type": "initial_state",
            "payload": {
                "devices": sim_engine.get_all_devices(),
                "status": sim_engine.get_full_status(),
                "system_state": event_bus.system_state,
            },
            "timestamp": time.time(),
        })

        # Keep connection alive and listen for commands
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                # Process incoming commands via WebSocket
                cmd = data.get("command")
                if cmd == "isolate":
                    result = await sim_engine.command_isolate(data.get("mac", ""))
                    await ws_manager.send_personal(websocket, {"type": "command_result", "payload": result})
                elif cmd == "release":
                    result = await sim_engine.command_release(data.get("mac", ""))
                    await ws_manager.send_personal(websocket, {"type": "command_result", "payload": result})
                elif cmd == "honeypot":
                    result = await sim_engine.command_deploy_honeypot(data.get("target_ip", ""), data.get("pot_type", "generic"))
                    await ws_manager.send_personal(websocket, {"type": "command_result", "payload": result})
                elif cmd == "set_state":
                    result = await sim_engine.command_set_state(data.get("state", ""))
                    await ws_manager.send_personal(websocket, {"type": "command_result", "payload": result})
                elif cmd == "set_speed":
                    sim_engine.set_speed(mode=data.get("mode"), custom_value=data.get("custom_value"))
                    await ws_manager.send_personal(websocket, {"type": "command_result", "payload": {"success": True}})
                elif cmd == "ping":
                    await ws_manager.send_personal(websocket, {"type": "pong", "timestamp": time.time()})
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({"type": "heartbeat", "timestamp": time.time()})
                except Exception:
                    break

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        ws_manager.disconnect(websocket)


# ─── MAIN ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)