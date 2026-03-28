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
    """Get recent alerts from database"""
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

@app.get("/traffic")
async def get_traffic_logs(limit: int = 100):
    """Get recent network traffic logs from database"""
    try:
        from core.database import db_manager, TrafficLog
        orchestrator = await get_orchestrator()
        session = db_manager.get_session()
        
        traffic_logs = session.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).limit(limit).all()
        db_manager.close_session(session)
        
        return {
            "traffic_logs": [{
                'id': log.id,
                'source_ip': log.source_ip,
                'destination_ip': log.destination_ip,
                'source_port': log.source_port,
                'destination_port': log.destination_port,
                'protocol': log.protocol,
                'packet_size': log.packet_size,
                'timestamp': log.timestamp.isoformat() if log.timestamp else None
            } for log in traffic_logs]
        }
    except Exception as e:
        logger.error(f"Error fetching traffic logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch traffic logs")

@app.get("/honeypots/detection")
async def get_honeypot_detection(limit: int = 100):
    """Get honeypot detection events from database"""
    try:
        from core.database import db_manager, HoneypotInteraction
        orchestrator = await get_orchestrator()
        session = db_manager.get_session()
        
        detections = session.query(HoneypotInteraction).order_by(HoneypotInteraction.timestamp.desc()).limit(limit).all()
        db_manager.close_session(session)
        
        return {
            "honeypot_detections": [{
                'id': det.id,
                'ip_address': det.ip_address,
                'threat_type': det.threat_type,
                'attack_type': det.attack_type,
                'honeypot_type': det.honeypot_type,
                'timestamp': det.timestamp.isoformat() if det.timestamp else None,
                'severity': det.severity
            } for det in detections]
        }
    except Exception as e:
        logger.error(f"Error fetching honeypot detections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch honeypot detections")

@app.get("/anomalies")
async def get_anomalies(limit: int = 100):
    """Get detected anomalies"""
    try:
        from core.database import db_manager, Alert
        orchestrator = await get_orchestrator()
        session = db_manager.get_session()
        
        anomalies = session.query(Alert).filter(Alert.alert_type.in_(['anomaly', 'high_traffic'])).order_by(Alert.timestamp.desc()).limit(limit).all()
        db_manager.close_session(session)
        
        return {
            "anomalies": [{
                'id': anom.id,
                'message': anom.message,
                'device_mac': anom.device_mac,
                'severity': anom.severity,
                'timestamp': anom.timestamp.isoformat() if anom.timestamp else None,
                'status': anom.status
            } for anom in anomalies]
        }
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch anomalies")

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
                "alerts": orchestrator.state.alerts[-20:],  # Last 20 alerts
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