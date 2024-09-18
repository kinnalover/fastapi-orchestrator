import uuid

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

from app.models import Trigger, Job
from datetime import datetime, timedelta
from celery.schedules import crontab
from app.worker import run_process
from celery.result import AsyncResult
from app.worker import celery_app as celery


@router.post("/")
def create_trigger(trigger: schemas.TriggerCreate, db: Session = Depends(get_db)):
    if not trigger.time:
        raise HTTPException(status_code=400, detail="Time must be provided for scheduling")

        # Extract hour and minute from the time string
    time_parts = trigger.time.split(':')
    hour = str(int(time_parts[0]))
    minute = str(int(time_parts[1]))

    celery_task = None
    identifier = str(uuid.uuid4())
    daily_name_prefix = 'daily-task-'
    working_days_name_prefix ='workingday-task-'
    custom_days_name_prefix = 'customday-task-'
    # Handle different scheduling types
    unique_id = ''
    if trigger.schedule_type == 'once':
        # Schedule the task once (example: 10 minutes from now)
        delay  = 5
        eta = datetime.now() + timedelta(seconds=delay)
        print(f"After {delay} seconds the task will be executed")
        celery_task = run_process.apply_async(args=['1', '2'])

    elif trigger.schedule_type == 'daily':
        # Schedule the task to run daily at the specified time
        unique_id= daily_name_prefix + identifier
        celery.conf.beat_schedule = {
            unique_id: {
                'task': 'tasks.run_process',
                'schedule': crontab(hour=str(hour), minute=str(minute)),
                'args': (str(trigger.process_id), str(trigger.machine_id))
            }
        }

    elif trigger.schedule_type == 'workingDays':
        # Schedule the task to run Monday to Friday at the specified time
        unique_id = working_days_name_prefix + identifier
        celery.conf.beat_schedule = {
            unique_id: {
                'task': 'tasks.run_process',
                'schedule': crontab(hour=hour, minute=minute, day_of_week='1-5'),
                'args': (str(trigger.process_id), str(trigger.machine_id))
            }
        }

    elif trigger.schedule_type == 'customDays':
        if not trigger.selected_days:
            raise HTTPException(status_code=400, detail="Custom days must be provided")
        unique_id = custom_days_name_prefix + identifier
        # Map days to crontab format
        day_mapping = {
            'Monday': '1', 'Tuesday': '2', 'Wednesday': '3',
            'Thursday': '4', 'Friday': '5', 'Saturday': '6', 'Sunday': '0'
        }
        days = ','.join([day_mapping[day] for day in trigger.selected_days])

        # Schedule the task to run on the selected days

        celery.conf.beat_schedule = {
            unique_id: {
                'task': 'tasks.run_process',
                'schedule': crontab(hour=hour, minute=minute, day_of_week=days),
                'args': (str(trigger.process_id), str(trigger.machine_id))
            }
        }


    else:
        raise HTTPException(status_code=400, detail="Invalid schedule type")

    # Now store the trigger and celery_task_id in the database
    new_trigger = Trigger(
        process_id=trigger.process_id,
        machine_id=trigger.machine_id,
        schedule_type=trigger.schedule_type,
        selected_days=','.join(trigger.selected_days) if trigger.selected_days else None,
        schedule_time=trigger.time,
        celery_task_id=celery_task.id if celery_task else unique_id # Store the Celery task ID
    )

    db.add(new_trigger)
    db.commit()
    db.refresh(new_trigger)
    print("task_id", celery_task.id if celery_task else unique_id)
    return {"message": "Task scheduled successfully", "celery_task_id": celery_task.id if celery_task else unique_id}

@router.get("/taskss/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id, app=celery)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
        "task_state": task_result.state
    }
    return JSONResponse(result)

@router.get("/")
def get_triggers(db: Session = Depends(get_db)):
    triggers = db.query(Trigger).all()
    return triggers


@router.get("/{trigger_id}")
def get_trigger(trigger_id: int, db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@router.put("/{trigger_id}")
def update_trigger(trigger_id: int, job_id: int, schedule_time: datetime, db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Revoke the old Celery task
    celery.control.revoke(trigger.celery_task_id)

    # Schedule the new task with updated schedule
    eta = schedule_time - datetime.now()
    celery_task = run_process.apply_async((job_id,), countdown=eta.total_seconds())

    # Update the trigger details
    trigger.job_id = job_id
    trigger.schedule_time = schedule_time
    trigger.celery_task_id = celery_task.id
    db.commit()
    db.refresh(trigger)

    return {"trigger_id": trigger.id, "celery_task_id": trigger.celery_task_id}


@router.delete("/{trigger_id}")
def delete_trigger(trigger_id: int, db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Revoke the Celery task
    celery.control.revoke(trigger.celery_task_id)

    # Delete the trigger from the database
    db.delete(trigger)
    db.commit()

    return {"message": "Trigger deleted"}
