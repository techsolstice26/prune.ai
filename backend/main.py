from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aws_client

app = FastAPI(title="CloudScope AIOps Delivery Layer")

# Enable CORS for the React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        # We now map connections by role_arn so we can direct alerts properly
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, role_arn: str):
        await websocket.accept()
        if role_arn not in self.active_connections:
            self.active_connections[role_arn] = []
        self.active_connections[role_arn].append(websocket)

    def disconnect(self, websocket: WebSocket, role_arn: str):
        if role_arn in self.active_connections and websocket in self.active_connections[role_arn]:
            self.active_connections[role_arn].remove(websocket)

    async def broadcast_alert(self, role_arn: str, message: dict):
        if role_arn in self.active_connections:
            for connection in self.active_connections[role_arn]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# --- Models ---
class AuthPayload(BaseModel):
    role_arn: str

class AlertPayload(BaseModel):
    role_arn: str
    instance_id: str
    suspicion_score: float
    narrative: dict
    metrics: dict

class RollbackPayload(BaseModel):
    role_arn: str
    instance_id: str

# --- HTTP Routes ---

@app.post("/api/auth/aws")
async def register_aws_account(payload: AuthPayload):
    """Authenticates the Front-End against an AWS Cross-Account Role."""
    
    # MAGIC DEMO STRING FOR HACKATHON
    if payload.role_arn == "arn:aws:iam::123456789012:role/demo":
        return {
            "status": "authenticated",
            "account_id": "123456789012 (DEMO)",
            "token": payload.role_arn
        }

    result = aws_client.verify_role_arn(payload.role_arn)
    if result.get("status") == "error":
        # In a real setup, we would actually validate this. For mock demo, if STS fails due to local env, we return it as a success for testing.
        if "No credentials" in result.get("message", ""):
            # Auto-mock success for UI sandbox
            return {
                "status": "authenticated",
                "account_id": "MOCK_LOCAL_ENV_ID",
                "token": payload.role_arn
            }
        raise HTTPException(status_code=401, detail=f"Invalid AWS Role Assumption: {result['message']}")
    
    return {
        "status": "authenticated",
        "account_id": result["account"],
        "token": payload.role_arn
    }

@app.post("/api/alert")
async def receive_explainer_alert(alert: AlertPayload):
    """Hidden endpoint called by the Explainer Lambda to push Gemini Narrative to a specific user."""
    await manager.broadcast_alert(alert.role_arn, alert.model_dump())
    return {"status": "alert_broadcast_successful", "delivered_to": alert.role_arn}

@app.post("/api/rollback")
async def trigger_rollback(payload: RollbackPayload):
    """Triggered when user clicks 'Undo' on React dashboard."""
    restart_resp = aws_client.restart_instance(payload.instance_id, payload.role_arn)
    snooze_resp = aws_client.add_to_snooze_registry(payload.instance_id)

    return {
        "rollback_status": "executed",
        "restart": restart_resp,
        "snooze": snooze_resp
    }

# --- WebSockets ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = "default_session"):
    """
    Endpoint for React Dashboard to connect and receive real-time alerts.
    The frontend query param 'token' passes the authenticated user's Role ARN.
    """
    role_arn = token
    await manager.connect(websocket, role_arn)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, role_arn)
