import asyncio

from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends
from fastapi.responses import HTMLResponse

router = APIRouter()
app = FastAPI()
from app.crud import update_machine_2, update_job_2, fetch_logs_for_job
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, client_ip):
        await websocket.accept()

        self.active_connections.update({client_ip: websocket})

    def disconnect(self, client_ip):
        if self.active_connections.get(client_ip):
            update_machine_2(client_ip, 'offline')
            del self.active_connections[client_ip]

    async def send_personal_message(self, message: str, ip_address):
        # print(f"sending message: {message} to {ip_address}")
        # print(f'active connections in send_personal: {self.active_connections}')
        websocket = self.active_connections.get(ip_address)
        if websocket:
            await websocket.send_text(message)
            print(f"sent message: {message}")

    async def send_message(self, message: str, ip_address):
        print(f"sending message: {message} to {ip_address}")
        print(f'active connections in send_personal: {self.active_connections}')
        websocket = self.active_connections.get(ip_address)
        if websocket:
            await websocket.send_text(message)
            print('sent custom message')
        else:
            print(f"NO websocket: {message} to {ip_address}")

    async def broadcast(self, message: str):
        for ip, connection in self.active_connections.items():
            # print(f'Connected: {ip}')
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'heartbeat':
                machine_id = message['machine_id']
                update_machine_2(machine_id, 'online')
                msg = json.dumps({"type": "heartbeat_ack", "status": "acknowledged"})

                await manager.send_personal_message(msg, client_id)
            if message['type'] == "process_result":
                print(message)
                error = None
                if message.get('stderr') is not None:
                    error = message.get('stderr')

                update_job_2(message.get('job_id'), message.get("status"), error)

            await manager.send_personal_message(data, client_id)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect as exwd:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat: {exwd}")
    except Exception as ex:
        manager.disconnect(client_id)
        print(f"Exception:{ex}")


@router.websocket("/logs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        # Continuously send logs from the database
        while True:
            logs, just_once = fetch_logs_for_job(job_id, db)  # You need to define this function
            for log in logs:
                log_data = {
                    "asctime": log.asctime.isoformat(),
                    "levelname": log.levelname,
                    "message": log.message,
                    "funcname": log.funcname,
                    "filename": log.filename,
                    "lineno": log.lineno,
                }
                await websocket.send_json(log_data)  # Convert log entry to a dictionary
            if just_once:
                break
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("sdfdsfdsfwegfkew websocket")


# Function to fetch logs from the database for a specific job (dummy example)
