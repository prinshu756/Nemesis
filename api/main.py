from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from core.orchestrator import NemesisOrchestrator
from core.logging_config import logger
from core.config import config
from api.database_service import db_service
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
            # Create device copy with all necessary fields
            device_copy = device.copy()
            
            # Ensure all required fields are present
            if 'mac' not in device_copy:
                device_copy['mac'] = mac
            if 'status' not in device_copy:
                device_copy['status'] = 'online'
            if 'health' not in device_copy:
                device_copy['health'] = 85
            if 'power_level' not in device_copy:
                device_copy['power_level'] = 85
            if 'hostname' not in device_copy:
                device_copy['hostname'] = f"Device-{mac.split(':')[-1].upper()}"
            if 'risk_score' not in device_copy:
                device_copy['risk_score'] = orchestrator.risk_engine.compute_risk(device)
            if 'risk_level' not in device_copy:
                device_copy['risk_level'] = _get_risk_level(device_copy.get('risk_score', 0))
            
            # Ensure ports is a list (convert from set if needed)
            if 'ports' in device_copy and isinstance(device_copy['ports'], set):
                device_copy['ports'] = list(device_copy['ports'])
            
            # Include mobile device information
            if device_copy.get('is_mobile'):
                device_copy['device_type'] = device_copy.get('mobile_device_type', 'Mobile Device')
            
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

@app.get("/beta/engagement-metrics")
async def get_beta_engagement_metrics():
    """Get Beta Agent engagement metrics"""
    try:
        orchestrator = await get_orchestrator()
        if not orchestrator.beta:
            raise HTTPException(status_code=503, detail="Agent Beta not available")
        
        metrics = orchestrator.beta.get_engagement_metrics()
        return {"metrics": metrics}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Beta metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch engagement metrics")

@app.get("/beta/honeytokens")
async def get_honeytokens():
    """Get honeytokens status and details"""
    try:
        orchestrator = await get_orchestrator()
        if not orchestrator.beta:
            raise HTTPException(status_code=503, detail="Agent Beta not available")
        
        tokens = orchestrator.beta.honeytoken_gen.honeytokens
        token_summary = {
            'total': len(tokens),
            'triggered': sum(1 for t in tokens.values() if t.get('triggered', False)),
            'active': sum(1 for t in tokens.values() if not t.get('triggered', False)),
            'tokens': {
                token_id: {
                    'type': t['data'].get('type'),
                    'created_at': t.get('created_at'),
                    'triggered': t.get('triggered', False),
                    'trigger_details': t.get('trigger_details')
                }
                for token_id, t in tokens.items()
            }
        }
        
        return {"honeytokens": token_summary}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching honeytokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch honeytokens")

@app.post("/beta/honeytokens/generate")
async def generate_honeytoken(token_type: str = 'random'):
    """Generate a new honeytoken"""
    try:
        orchestrator = await get_orchestrator()
        if not orchestrator.beta:
            raise HTTPException(status_code=503, detail="Agent Beta not available")
        
        honeytoken = orchestrator.beta.honeytoken_gen.generate_honeytoken(token_type)
        return {
            "message": f"Honeytoken generated",
            "honeytoken_id": honeytoken['id'],
            "type": honeytoken['data'].get('type'),
            "created_at": honeytoken['created_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating honeytoken: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate honeytoken")

@app.get("/beta/engagement-report")
async def get_beta_report():
    """Get comprehensive Beta Agent engagement report"""
    try:
        orchestrator = await get_orchestrator()
        if not orchestrator.beta:
            raise HTTPException(status_code=503, detail="Agent Beta not available")
        
        report = orchestrator.beta.get_engagement_report()
        return {"report": report}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Beta report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

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

# ============= DATABASE PERSISTENCE ENDPOINTS =============

@app.post("/db/devices")
async def save_devices_to_db():
    """Save all discovered devices to database"""
    try:
        orchestrator = await get_orchestrator()
        saved_count = 0
        
        for mac, device in orchestrator.state.devices.items():
            try:
                risk_score = orchestrator.risk_engine.compute_risk(device)
                device_data = {
                    'mac': mac,
                    'ip': device.get('ip'),
                    'hostname': device.get('hostname'),
                    'device_type': device.get('device_type', 'unknown'),
                    'vendor': device.get('vendor', 'unknown'),
                    'risk_score': risk_score,
                    'risk_level': _get_risk_level(risk_score),
                    'is_active': device.get('is_active', True),
                    'os_fingerprint': device.get('os_fingerprint')
                }
                
                if db_service.persist_device(device_data):
                    saved_count += 1
            except Exception as e:
                logger.error(f"Error saving device {mac}: {e}")
        
        return {
            "message": f"Saved {saved_count} devices to database",
            "saved_count": saved_count,
            "total_devices": len(orchestrator.state.devices)
        }
    except Exception as e:
        logger.error(f"Error saving devices to database: {e}")
        raise HTTPException(status_code=500, detail="Failed to save devices to database")

@app.post("/db/alerts")
async def save_alerts_to_db():
    """Save all alerts to database"""
    try:
        orchestrator = await get_orchestrator()
        saved_count = 0
        
        for alert in orchestrator.state.alerts:
            try:
                alert_data = {
                    'message': alert.get('message', 'No message'),
                    'severity': alert.get('severity', 'medium'),
                    'type': alert.get('type', 'generic'),
                    'device_mac': alert.get('device_mac'),
                    'details': alert.get('details', {})
                }
                
                if db_service.persist_alert(alert_data):
                    saved_count += 1
            except Exception as e:
                logger.error(f"Error saving alert: {e}")
        
        return {
            "message": f"Saved {saved_count} alerts to database",
            "saved_count": saved_count,
            "total_alerts": len(orchestrator.state.alerts)
        }
    except Exception as e:
        logger.error(f"Error saving alerts to database: {e}")
        raise HTTPException(status_code=500, detail="Failed to save alerts to database")

@app.post("/db/device/{mac}")
async def save_single_device_to_db(mac: str):
    """Save a specific device to database"""
    try:
        orchestrator = await get_orchestrator()
        if mac not in orchestrator.state.devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device = orchestrator.state.devices[mac]
        risk_score = orchestrator.risk_engine.compute_risk(device)
        device_data = {
            'mac': mac,
            'ip': device.get('ip'),
            'hostname': device.get('hostname'),
            'device_type': device.get('device_type', 'unknown'),
            'vendor': device.get('vendor', 'unknown'),
            'risk_score': risk_score,
            'risk_level': _get_risk_level(risk_score),
            'is_active': device.get('is_active', True),
            'os_fingerprint': device.get('os_fingerprint')
        }
        
        if db_service.persist_device(device_data):
            return {
                "message": f"Device {mac} saved to database",
                "mac": mac,
                "success": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save device")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving device {mac}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save device to database")

@app.post("/db/alert")
async def save_alert_to_db(alert_data: dict):
    """Save a specific alert to database"""
    try:
        if db_service.persist_alert(alert_data):
            return {
                "message": "Alert saved to database",
                "success": True,
                "data": alert_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save alert")
    except Exception as e:
        logger.error(f"Error saving alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to save alert to database")

@app.post("/db/traffic")
async def save_traffic_to_db(traffic_data: dict):
    """Save traffic log to database"""
    try:
        if db_service.persist_traffic_log(traffic_data):
            return {
                "message": "Traffic log saved to database",
                "success": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save traffic log")
    except Exception as e:
        logger.error(f"Error saving traffic log: {e}")
        raise HTTPException(status_code=500, detail="Failed to save traffic log to database")

@app.post("/db/honeypot-interaction")
async def save_honeypot_interaction_to_db(interaction_data: dict):
    """Save honeypot interaction to database"""
    try:
        if db_service.persist_honeypot_interaction(interaction_data):
            return {
                "message": "Honeypot interaction saved to database",
                "success": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save honeypot interaction")
    except Exception as e:
        logger.error(f"Error saving honeypot interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to save honeypot interaction to database")

# ============= DATABASE RETRIEVAL ENDPOINTS =============

@app.get("/db/devices")
async def get_persisted_devices(limit: int = 100):
    """Get all persisted devices from database"""
    try:
        devices = db_service.get_devices(limit)
        return {
            "devices": devices,
            "count": len(devices),
            "source": "database"
        }
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve devices from database")

@app.get("/db/alerts")
async def get_persisted_alerts(limit: int = 100):
    """Get all persisted alerts from database"""
    try:
        alerts = db_service.get_alerts(limit)
        return {
            "alerts": alerts,
            "count": len(alerts),
            "source": "database"
        }
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts from database")

@app.get("/db/traffic")
async def get_persisted_traffic(limit: int = 100):
    """Get all persisted traffic logs from database"""
    try:
        logs = db_service.get_traffic_logs(limit)
        return {
            "traffic_logs": logs,
            "count": len(logs),
            "source": "database"
        }
    except Exception as e:
        logger.error(f"Error retrieving traffic logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve traffic logs from database")

@app.get("/db/honeypot-interactions")
async def get_persisted_honeypot_interactions(limit: int = 100):
    """Get all persisted honeypot interactions from database"""
    try:
        interactions = db_service.get_honeypot_interactions(limit)
        return {
            "honeypot_interactions": interactions,
            "count": len(interactions),
            "source": "database"
        }
    except Exception as e:
        logger.error(f"Error retrieving honeypot interactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve honeypot interactions from database")

@app.get("/db/status")
async def get_database_status():
    """Get database connectivity status"""
    try:
        local_status = "connected"
        neon_status = "connected" if db_service.neon_db else "not_configured"
        
        return {
            "local_db": {
                "status": local_status,
                "type": "SQLite",
                "url": os.getenv('DATABASE_URL', 'sqlite:///./nemesis.db')
            },
            "neon_db": {
                "status": neon_status,
                "type": "PostgreSQL",
                "url": "***configured***" if os.getenv('NEON_DATABASE_URL') else "not_configured"
            }
        }
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database status")

@app.get("/backend/status")
async def get_comprehensive_backend_status():
    """Get comprehensive backend status including all running processes and data"""
    try:
        import time
        
        # Try to import psutil, fall back if not available
        try:
            import psutil
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
        except ImportError:
            cpu_percent = 0.0
            memory_mb = 0.0
        
        orchestrator = await get_orchestrator()
        
        # Device metrics
        device_count = len(orchestrator.state.devices)
        active_devices = sum(1 for d in orchestrator.state.devices.values() if d.get('is_active', True))
        
        # Risk assessment
        high_risk_devices = sum(1 for d in orchestrator.state.devices.values() 
                               if d.get('risk_level') in ['high', 'critical'])
        
        # Alert metrics
        alert_count = len(orchestrator.state.alerts)
        critical_alerts = sum(1 for a in orchestrator.state.alerts 
                             if a.get('severity') == 'critical')
        high_alerts = sum(1 for a in orchestrator.state.alerts 
                         if a.get('severity') == 'high')
        
        # Get honeypot info
        try:
            honeypots = orchestrator.beta.get_active_honeypots() if hasattr(orchestrator, 'beta') else []
        except:
            honeypots = []
        
        # Get policies
        try:
            policies = orchestrator.gamma.get_segmentation_status() if hasattr(orchestrator, 'gamma') else {}
        except:
            policies = {}
        
        # Database stats
        try:
            session = db_service.local_db.get_session()
            from core.database import Device, Alert, TrafficLog, HoneypotInteraction
            
            db_device_count = session.query(Device).count()
            db_alert_count = session.query(Alert).count()
            db_traffic_count = session.query(TrafficLog).count()
            db_honeypot_count = session.query(HoneypotInteraction).count()
            
            db_service.local_db.close_session(session)
        except:
            db_device_count = db_alert_count = db_traffic_count = db_honeypot_count = 0
        
        return {
            "timestamp": time.time(),
            "system": {
                "status": orchestrator.get_status() if hasattr(orchestrator, 'get_status') else "running",
                "cpu_usage_percent": cpu_percent,
                "memory_usage_mb": round(memory_mb, 2),
                "uptime": "N/A"
            },
            "network_monitoring": {
                "total_devices": device_count,
                "active_devices": active_devices,
                "high_risk_devices": high_risk_devices,
                "devices_isolated": sum(1 for d in orchestrator.state.devices.values() 
                                       if d.get('isolation_status') != 'normal')
            },
            "alerts": {
                "total_alerts": alert_count,
                "critical": critical_alerts,
                "high": high_alerts,
                "medium": sum(1 for a in orchestrator.state.alerts 
                             if a.get('severity') == 'medium'),
                "low": sum(1 for a in orchestrator.state.alerts 
                          if a.get('severity') == 'low')
            },
            "honeypots": {
                "active_count": len(honeypots) if isinstance(honeypots, list) else 0,
                "honeypots": honeypots
            },
            "security_policies": {
                "total_policies": len(policies) if isinstance(policies, dict) else 0,
                "policies": policies
            },
            "agents": {
                "alpha": {
                    "name": "Network Discovery & Scanning",
                    "status": "active" if hasattr(orchestrator, 'alpha') else "inactive",
                    "function": "Real-time network scanning and device discovery"
                },
                "beta": {
                    "name": "Honeypot Deployment & Threat Capture",
                    "status": "active" if hasattr(orchestrator, 'beta') else "inactive",
                    "function": "Deploy and manage honeypots for threat detection"
                },
                "gamma": {
                    "name": "Adaptive Segmentation & Response",
                    "status": "active" if hasattr(orchestrator, 'gamma') else "inactive",
                    "function": "Implement segmentation policies and containment"
                }
            },
            "database": {
                "local": {
                    "type": "SQLite",
                    "devices": db_device_count,
                    "alerts": db_alert_count,
                    "traffic_logs": db_traffic_count,
                    "honeypot_interactions": db_honeypot_count,
                    "total_records": db_device_count + db_alert_count + db_traffic_count + db_honeypot_count
                },
                "neon": {
                    "type": "PostgreSQL Cloud",
                    "status": "connected" if db_service.neon_db else "not_configured",
                    "url": "***configured***" if os.getenv('NEON_DATABASE_URL') else "not_configured"
                }
            },
            "recent_events": {
                "latest_devices": list(orchestrator.state.devices.values())[:5] if orchestrator.state.devices else [],
                "latest_alerts": orchestrator.state.alerts[:5] if orchestrator.state.alerts else [],
                "total_threats_detected": len(orchestrator.state.alerts)
            }
        }
    except Exception as e:
        logger.error(f"Error getting comprehensive backend status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get backend status")

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