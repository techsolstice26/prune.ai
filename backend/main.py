from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import aws_client
import json

app = FastAPI(title="CloudScope AIOps Delivery Layer")

# In-memory store of active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_alert(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

class AlertPayload(BaseModel):
    instance_id: str
    suspicion_score: float
    narrative: str
    metrics: dict

class RollbackPayload(BaseModel):
    instance_id: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint for React Dashboard to connect and receive real-time alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # We just keep the connection alive. React UI doesn't need to send messages here.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/alert")
async def receive_explainer_alert(alert: AlertPayload):
    """Hidden endpoint called by the Explainer Lambda to push Gemini Narrative."""
    # Instantly push to all connected WebSockets
    await manager.broadcast_alert(alert.model_dump())
    return {"status": "alert_broadcast_successful"}

@app.post("/api/rollback")
async def trigger_rollback(payload: RollbackPayload):
    """Triggered when user clicks 'Undo' on React dashboard."""
    # 1. Restart Instance via Boto3
    restart_resp = aws_client.restart_instance(payload.instance_id)
    
    # 2. Add to Snooze Registry
    snooze_resp = aws_client.add_to_snooze_registry(payload.instance_id)

    return {
        "rollback_status": "executed",
        "restart": restart_resp,
        "snooze": snooze_resp
    }
