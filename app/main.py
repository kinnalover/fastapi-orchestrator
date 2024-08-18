from fastapi import FastAPI
from routers import processes, machines, jobs, tasks, schedules, users, triggers
import uvicorn
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your SvelteKit app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(processes.router, prefix="/processes", tags=["processes"])
app.include_router(machines.router, prefix="/machines", tags=["machines"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(triggers.router, prefix="/triggers", tags=["triggers"])

if __name__ == '__main__':
    uvicorn.run(app, host= 'localhost', port=5000)