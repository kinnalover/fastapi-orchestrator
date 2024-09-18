import threading
import time
from typing import Dict
from fastapi import FastAPI
from routers import processes, machines, jobs, tasks, schedules, users, triggers
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
import asyncio
app = FastAPI()
from database import  get_db_2
from models import Job, Machine, Process
from fastapi.middleware.cors import CORSMiddleware
import websocket
import json
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your SvelteKit app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
loop = asyncio.get_event_loop()
app.include_router(processes.router, prefix="/processes", tags=["processes"])
app.include_router(machines.router, prefix="/machines", tags=["machines"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(triggers.router, prefix="/triggers", tags=["triggers"])
app.include_router(websocket.router, prefix="/ws", tags=['ws'])
from websocket import manager
message_queue = asyncio.Queue()

# WebSocket manager (assumed to be part of your app, this manages WebSocket connections)
# Replace this with your actual WebSocket manager implementation

def run_background_worker(loop):
    """Blocking background worker, which handles database queries."""
    asyncio.set_event_loop(loop)  # Ensure the correct event loop is set
    while True:
        print("Starting job check")
        with get_db_2() as db:
            pending_jobs = db.query(Job).filter(Job.status == 'pending').all()

            for job in pending_jobs:
                print(job.__dict__)
                machine = db.query(Machine).filter(Machine.id == job.machine_id).first()
                process = db.query(Process).filter(Process.id == job.process_id).first()

                if not machine:
                    print("No such machine")
                    continue

                print('Active connection present')
                msg = {
                    "type": "run_process",
                    "machine_id": machine.ip_address,
                    "gitlab_repo": process.repository_url,
                    "job_id": str(job.id),
                    "timestamp": int(time.time())
                }
                # Pass message to the asyncio queue
                asyncio.run_coroutine_threadsafe(message_queue.put((json.dumps(msg), machine.ip_address)), loop)

        print("Sleeping for 20 seconds")
        time.sleep(20)


async def websocket_worker():
    """Asynchronous coroutine to handle WebSocket communication."""
    while True:
        # Get message from the queue (blocking for the asyncio event loop)
        message, machine_ip = await message_queue.get()
        try:
            # Send the message via WebSocket
            print('Sending message')
            await manager.send_message(message, machine_ip)
        except Exception as e:
            print(f"Error sending message via WebSocket: {e}")
        finally:
            message_queue.task_done()  # Mark the task as done


@app.on_event("startup")
async def startup_event():
    """Start background worker in a separate thread and WebSocket worker in the event loop."""
    loop = asyncio.get_running_loop()  # Get the running event loop

    # Run the background worker in a separate thread
    worker_thread = threading.Thread(target=run_background_worker, args=(loop,), daemon=True)
    worker_thread.start()

    # Start the asynchronous WebSocket worker
    asyncio.create_task(websocket_worker())


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=5000)
