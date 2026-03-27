from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from core.orchestrator import NemesisOrchestrator
from core.logging_config import logger
from core.config import config
import uvicorn

app = FastAPI(
    title="Nemesis Network Security API",
    description="AI-powered network threat detection and response system",
    version="2.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of orchestrator
orch = None

async def get_orchestrator():
    """Get or initialize the orchestrator"""
    global orch
    if orch is None:
        logger.info("Initializing orchestrator...")
        orch = NemesisOrchestrator()
        logger.info("Orchestrator initialized")
    return orch

@app.on_event("startup")
async def startup():
    """Initialize the system on startup"""
    logger.info("Starting Nemesis API server")
    orchestrator = await get_orchestrator()
    asyncio.create_task(orchestrator.run())

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down Nemesis API server")
    # Emergency cleanup would happen in orchestrator

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Nemesis Network Security System API",
        "version": "2.0.0",
        "status": "active"
    }

@app.get("/devices")
async def devices():
    """Get all discovered devices"""
    try:
        orchestrator = await get_orchestrator()
        devices = []
        for mac, device in orchestrator.state.devices.items():
            # Add computed risk score
            risk_score = orchestrator.risk_engine.compute_risk(device)
            device_copy = device.copy()
            device_copy['risk_score'] = risk_score
            device_copy['mac'] = mac
            devices.append(device_copy)

        return {"devices": devices, "count": len(devices)}
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch devices")

@app.get("/devices/{mac}")
async def device_detail(mac: str):
    """Get detailed information about a specific device"""
    try:
        orchestrator = await get_orchestrator()
        if mac not in orchestrator.state.devices:
            raise HTTPException(status_code=404, detail="Device not found")

        device = orchestrator.state.devices[mac]
        risk_score = orchestrator.risk_engine.compute_risk(device)

        return {
            "mac": mac,
            "device": device,
            "risk_score": risk_score,
            "risk_level": _get_risk_level(risk_score)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching device {mac}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch device")

@app.get("/alerts")
async def alerts():
    """Get recent alerts"""
    try:
        orchestrator = await get_orchestrator()
        alerts = orchestrator.get_recent_alerts(limit=50)
        return {"alerts": alerts}
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@app.get("/status")
async def system_status():
    """Get comprehensive system status"""
    try:
        orchestrator = await get_orchestrator()
        status = orchestrator.get_status()
        status.update({
            "uptime": "N/A",  # Could be enhanced with actual uptime tracking
            "config": {
                "interface": config.get('network.interface'),
                "ebpf_enabled": config.get('ebpf.enabled'),
                "ai_enabled": config.get('ai.use_local_ai')
            }
        })
        return status
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system status")

@app.post("/devices/{mac}/isolate")
async def isolate_device(mac: str, policy: str = "full_isolation"):
    """Manually isolate a device"""
    try:
        orchestrator = await get_orchestrator()
        if mac not in orchestrator.state.devices:
            raise HTTPException(status_code=404, detail="Device not found")

        orchestrator.gamma.isolate_device(mac, policy)

        return {
            "message": f"Device {mac} isolated with policy: {policy}",
            "policy": policy
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error isolating device {mac}: {e}")
        raise HTTPException(status_code=500, detail="Failed to isolate device")

@app.post("/devices/{mac}/honeypot")
async def deploy_honeypot(mac: str):
    """Deploy honeypot for a device"""
    try:
        orchestrator = await get_orchestrator()
        if mac not in orchestrator.state.devices:
            raise HTTPException(status_code=404, detail="Device not found")

        device = orchestrator.state.devices[mac]
        ip = device.get('ip')
        if not ip:
            raise HTTPException(status_code=400, detail="Device has no IP address")

        threat_type = "generic"  # Could be enhanced with threat classification
        container = orchestrator.beta.deploy_honeypot(ip, threat_type)

        if container:
            return {
                "message": f"Honeypot deployed for {mac} ({ip})",
                "container": container,
                "threat_type": threat_type
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to deploy honeypot")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying honeypot for {mac}: {e}")
        raise HTTPException(status_code=500, detail="Failed to deploy honeypot")

@app.get("/honeypots")
async def get_honeypots():
    """Get active honeypots"""
    try:
        orchestrator = await get_orchestrator()
        return {"honeypots": orchestrator.beta.get_active_honeypots()}
    except Exception as e:
        logger.error(f"Error fetching honeypots: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch honeypots")

@app.get("/policies")
async def get_policies():
    """Get current segmentation policies"""
    try:
        orchestrator = await get_orchestrator()
        return {"policies": orchestrator.gamma.get_segmentation_status()}
    except Exception as e:
        logger.error(f"Error fetching policies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch policies")
@app.get("/devices/stats")
async def device_statistics():
    """Get device statistics from database"""
    try:
        orchestrator = await get_orchestrator()
        stats = orchestrator.get_device_stats()
        return {"device_stats": stats}
    except Exception as e:
        logger.error(f"Error fetching device statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch device statistics")

@app.get("/traffic/logs")
async def traffic_logs(limit: int = 100):
    """Get recent traffic logs from database"""
    try:
        orchestrator = await get_orchestrator()
        from core.database import TrafficLog
        # Get traffic logs from database
        logs = orchestrator.db_session.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).limit(limit).all()

        traffic_data = [{
            'id': log.id,
            'source_ip': log.source_ip,
            'destination_ip': log.destination_ip,
            'source_port': log.source_port,
            'destination_port': log.destination_port,
            'protocol': log.protocol,
            'packet_size': log.packet_size,
            'flags': log.flags,
            'timestamp': log.timestamp.isoformat(),
            'details': log.details
        } for log in logs]

        return {"traffic_logs": traffic_data}
    except Exception as e:
        logger.error(f"Error fetching traffic logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch traffic logs")

@app.get("/honeypots/active")
async def active_honeypots():
    """Get active honeypot deployments"""
    try:
        orchestrator = await get_orchestrator()
        from core.database import HoneypotInteraction
        # Get active honeypots from database
        honeypots = orchestrator.db_session.query(HoneypotInteraction).filter_by(interaction_type='deployed').all()

        honeypot_data = [{
            'id': hp.id,
            'ip_address': hp.ip_address,
            'threat_type': hp.threat_type,
            'container_id': hp.container_id,
            'timestamp': hp.timestamp.isoformat(),
            'details': hp.details
        } for hp in honeypots]

        return {"active_honeypots": honeypot_data}
    except Exception as e:
        logger.error(f"Error fetching active honeypots: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch active honeypots")
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        orchestrator = await get_orchestrator()
        while True:
            # Send current state
            data = {
                "devices": _prepare_devices_data(orchestrator),
                "alerts": orchestrator.get_recent_alerts(limit=20),  # Last 20 alerts from database
                "status": orchestrator.get_status(),
                "timestamp": asyncio.get_event_loop().time()
            }

            await websocket.send_json(data)
            await asyncio.sleep(1)  # Update every second

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")

def _prepare_devices_data(orchestrator):
    """Prepare device data for WebSocket transmission"""
    devices = []
    for mac, device in orchestrator.state.devices.items():
        try:
            risk_score = orchestrator.risk_engine.compute_risk(device)
            device_copy = device.copy()
            device_copy['mac'] = mac
            device_copy['risk_score'] = risk_score
            device_copy['risk_level'] = _get_risk_level(risk_score)
            devices.append(device_copy)
        except Exception as e:
            logger.error(f"Error preparing device data for {mac}: {e}")
    return devices

def _get_risk_level(score):
    """Convert risk score to risk level"""
    if score >= 80:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 20:
        return "medium"
    else:
        return "low"

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )