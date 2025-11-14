"""
Security Monitoring Agent System - Main Application
FastAPI backend with WebSocket support for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
import asyncio
from datetime import datetime

from agents.network_monitor import NetworkMonitorAgent
from agents.attack_simulator import AttackSimulatorAgent
from agents.ai_coordinator import AIResponseCoordinator
from utils.notifications import notification_service
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Security Monitoring Agent System",
    description="AI-powered security monitoring and attack simulation platform",
    version="1.0.0"
)

# CORS middleware - configurable via environment
allowed_origins = ["*"] if settings.ALLOWED_ORIGINS == "*" else [
    origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instances
agents: Dict[str, Any] = {}
websocket_connections: List[WebSocket] = []

# Configure logging
logger.add(
    settings.LOG_FILE,
    rotation=settings.LOG_ROTATION,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    logger.info("🚀 Starting Security Monitoring Agent System...")

    try:
        # Initialize agents
        agents["network_monitor"] = NetworkMonitorAgent(
            interface=settings.NETWORK_INTERFACE,
            broadcast_callback=broadcast_alert
        )
        agents["attack_simulator"] = AttackSimulatorAgent()
        agents["ai_coordinator"] = AIResponseCoordinator()

        # Start core agents
        await agents["attack_simulator"].start()
        await agents["ai_coordinator"].start()

        # Network monitor starts on demand
        logger.success("✅ All agents initialized successfully")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Security Monitoring Agent System...")

    for name, agent in agents.items():
        try:
            await agent.stop()
            logger.info(f"✓ Stopped {name}")
        except Exception as e:
            logger.error(f"❌ Error stopping {name}: {e}")


# ============================================================================
# API Routes
# ============================================================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "running",
        "message": "Security Monitoring Agent System API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    statuses = {}

    for name, agent in agents.items():
        try:
            statuses[name] = await agent.get_status()
        except Exception as e:
            statuses[name] = {"error": str(e)}

    return statuses


@app.get("/api/agents/{agent_name}/health")
async def agent_health_check(agent_name: str):
    """Health check for specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    return await agents[agent_name].health_check()


# ============================================================================
# Network Monitor Routes
# ============================================================================

@app.post("/api/network-monitor/start")
async def start_network_monitor():
    """Start network monitoring"""
    try:
        await agents["network_monitor"].start()
        return {"status": "started", "message": "Network monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/network-monitor/stop")
async def stop_network_monitor():
    """Stop network monitoring"""
    try:
        await agents["network_monitor"].stop()
        return {"status": "stopped", "message": "Network monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/network-monitor/statistics")
async def get_network_statistics():
    """Get network monitoring statistics"""
    return await agents["network_monitor"].get_statistics()


@app.get("/api/network-monitor/alerts")
async def get_network_alerts(limit: int = 10):
    """Get recent network alerts"""
    return await agents["network_monitor"].get_recent_alerts(limit)


# ============================================================================
# Attack Simulator Routes
# ============================================================================

@app.post("/api/attack-simulator/port-scan")
async def simulate_port_scan(
    target: str,
    ports: List[int] = None,
    scan_type: str = "syn"
):
    """Simulate port scanning attack"""
    if not settings.ENABLE_ATTACK_SIM:
        raise HTTPException(status_code=403, detail="Attack simulation is disabled")

    return await agents["attack_simulator"].simulate_port_scan(
        target=target,
        ports=ports,
        scan_type=scan_type
    )


@app.post("/api/attack-simulator/ddos")
async def simulate_ddos(
    target: str,
    duration: int = 10,
    packet_rate: int = 100
):
    """Simulate DDoS attack"""
    if not settings.ENABLE_ATTACK_SIM:
        raise HTTPException(status_code=403, detail="Attack simulation is disabled")

    if duration > settings.MAX_SIMULATION_DURATION:
        raise HTTPException(
            status_code=400,
            detail=f"Duration exceeds maximum ({settings.MAX_SIMULATION_DURATION}s)"
        )

    return await agents["attack_simulator"].simulate_ddos(
        target=target,
        duration=duration,
        packet_rate=packet_rate
    )


@app.post("/api/attack-simulator/ping-sweep")
async def simulate_ping_sweep(network: str):
    """Simulate network ping sweep"""
    if not settings.ENABLE_ATTACK_SIM:
        raise HTTPException(status_code=403, detail="Attack simulation is disabled")

    return await agents["attack_simulator"].simulate_ping_sweep(network=network)


@app.get("/api/attack-simulator/simulations")
async def get_simulations(limit: int = 10):
    """Get recent attack simulations"""
    return await agents["attack_simulator"].get_simulations(limit)


@app.post("/api/attack-simulator/stop")
async def stop_simulation():
    """Stop current running simulation"""
    return await agents["attack_simulator"].stop_simulation()


# ============================================================================
# AI Coordinator Routes
# ============================================================================

@app.post("/api/ai/analyze")
async def analyze_incident(incident: Dict[str, Any]):
    """Analyze security incident with AI"""
    result = await agents["ai_coordinator"].analyze_incident(incident)

    # Send notification for medium, high, or critical severity
    severity = result.get("ai_analysis", {}).get("severity", "").lower()
    if severity in ["medium", "high", "critical"]:
        try:
            await notification_service.send_alert(
                incident=result.get("original_incident", incident),
                severity=severity
            )
            logger.info(f"📢 Alert notification sent for {result.get('incident_id')} (severity: {severity})")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    return result


class ReportRequest(BaseModel):
    incident_ids: Optional[List[str]] = None
    timeframe: Optional[str] = "24h"

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []

@app.post("/api/ai/chat")
async def chat_with_roma(request: ChatRequest):
    """Chat with Roma AI Assistant"""
    try:
        from agents.ai_service import ai_service

        system_prompt = """You are Roma, an expert AI cybersecurity assistant. You help users understand:
- Security threats and vulnerabilities
- Incident analysis and response
- Best practices for network security
- Attack prevention and mitigation
- Security tools and technologies

Provide clear, concise, and actionable advice. Use examples when helpful.
Be friendly and professional. Your responses should be informative but easy to understand."""

        response_text = await ai_service.generate_text(
            prompt=request.message,
            system_prompt=system_prompt
        )

        return {
            "response": response_text,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/report")
async def generate_report(request: ReportRequest):
    """Generate incident report"""
    report = await agents["ai_coordinator"].generate_report(
        incident_ids=request.incident_ids,
        timeframe=request.timeframe
    )
    return {"report": report, "timestamp": datetime.now().isoformat()}


@app.get("/api/ai/statistics")
async def get_ai_statistics():
    """Get AI coordinator statistics"""
    return await agents["ai_coordinator"].get_statistics()


# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time agent updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"🔌 WebSocket connected. Total connections: {len(websocket_connections)}")

    try:
        while True:
            # Send periodic updates
            status_update = {
                "timestamp": datetime.now().isoformat(),
                "agents": {}
            }

            for name, agent in agents.items():
                try:
                    status_update["agents"][name] = await agent.get_status()
                except Exception as e:
                    status_update["agents"][name] = {"error": str(e)}

            await websocket.send_json(status_update)
            await asyncio.sleep(2)  # Update every 2 seconds

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info(f"🔌 WebSocket disconnected. Remaining: {len(websocket_connections)}")


async def broadcast_alert(alert: Dict[str, Any]):
    """Broadcast alert to all connected WebSocket clients"""
    message = {
        "type": "alert",
        "data": alert,
        "timestamp": datetime.now().isoformat()
    }

    disconnected = []
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
            logger.debug(f"✓ Alert broadcasted to WebSocket client")
        except Exception as e:
            logger.error(f"Failed to send alert to WebSocket: {e}")
            disconnected.append(connection)

    # Remove disconnected clients
    for conn in disconnected:
        websocket_connections.remove(conn)


async def broadcast_update(update_type: str, data: Dict[str, Any]):
    """Broadcast general updates to all connected WebSocket clients"""
    message = {
        "type": "update",
        "update_type": update_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

    disconnected = []
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send update to WebSocket: {e}")
            disconnected.append(connection)

    # Remove disconnected clients
    for conn in disconnected:
        websocket_connections.remove(conn)


# ============================================================================
# Dashboard / System Routes
# ============================================================================

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get dashboard overview data"""
    network_stats = await agents["network_monitor"].get_statistics() if agents["network_monitor"].is_running else {}
    ai_stats = await agents["ai_coordinator"].get_statistics()

    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "uptime": (datetime.now() - agents["ai_coordinator"].start_time).total_seconds() if agents["ai_coordinator"].start_time else 0,
            "active_agents": sum(1 for a in agents.values() if a.is_running)
        },
        "network": network_stats,
        "ai": ai_stats
    }


if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment (Railway sets PORT env var)
    port = int(os.environ.get("PORT", settings.API_PORT))
    
    logger.info("🚀 Starting Security Monitoring Agent System API...")
    logger.info(f"📡 Host: {settings.API_HOST}:{port}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=port,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
