import uuid

from sqlalchemy.orm import Session
from . import models, schemas
import datetime
from database import SessionLocal, get_db_2
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Process CRUD operations
def get_process(db: Session, process_id: int):
    return db.query(models.Process).filter(models.Process.id == process_id).first()


def get_processes(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Process).offset(skip).limit(limit).all()


def create_process(db: Session, process: schemas.ProcessCreate):
    print(process.dict())
    db_process = models.Process(**process.dict())
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


def update_process(db: Session, process_id: int, process: schemas.ProcessUpdate):
    db_process = get_process(db, process_id)
    if db_process:
        for key, value in process.dict(exclude_unset=True).items():
            setattr(db_process, key, value)
        db.commit()
        db.refresh(db_process)
    return db_process


def delete_process(db: Session, process_id: int):
    db_process = get_process(db, process_id)
    if db_process:
        db.delete(db_process)
        db.commit()


# Machine CRUD operations
def get_machine(db: Session, machine_id: int):
    return db.query(models.Machine).filter(models.Machine.id == machine_id).first()


def get_machine_by_ip(db: Session, machine_ip: str):
    return db.query(models.Machine).filter(models.Machine.ip_address == machine_ip).first()


def get_machines(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Machine).offset(skip).limit(limit).all()


def create_machine(db: Session, machine: schemas.MachineCreate):
    db_machine = models.Machine(**machine.dict())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


def update_machine(db: Session, machine_id, status):
    db_machine = get_machine(db, machine_id)
    if db_machine:
        db_machine.status = status
        update_row_model(db_machine)
    return db_machine


def update_machine_2(machine_id, status):
    db = SessionLocal()
    db_machine = get_machine_by_ip(db, machine_id)
    if db_machine:
        if status == 'online':
            db_machine.last_heartbeat = datetime.datetime.now()
        db_machine.status = status

        db.commit()

    db.close()
    return db_machine


def delete_machine(db: Session, machine_id: int):
    db_machine = get_machine(db, machine_id)
    if db_machine:
        db.delete(db_machine)
        db.commit()


# Job CRUD operations
def get_job(db: Session, job_id):
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def get_job_by_process_id(db: Session, process_id: uuid.UUID):
    return db.query(models.Job).filter(models.Job.process_id == process_id).all()


def get_jobs(db: Session, skip: int = 0, limit: int = 10):
    jobs =db.query(models.Job).order_by(desc(models.Job.start_time)).all()
    return jobs


def fetch_logs_for_job(job_id: str, db):
    job = get_job(db, job_id)
    # TODO get machine id
    machine = get_machine(db, job.machine_id)
    machine_ip = machine.ip_address
    if machine_ip == '172.30.201.19':
        machine_ip = 'localhost'
    new_url = f"postgresql://postgres:password@{machine_ip}:5432/postgres"
    engine = create_engine(new_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    just_once = False
    if job.end_time:
        just_once = True
        print("Дата конца уже есть")
        filter = and_(models.RPALog.asctime >= job.start_time, models.RPALog.asctime <= job.end_time)
    else:
        print("Дата конца нет")
        filter = models.RPALog.asctime >= job.start_time - datetime.timedelta(minutes=2)
    with SessionLocal() as db:
        data = db.query(models.RPALog).filter(filter).all()
        print(f'data length: {len(data)}')
        return data, just_once


def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(**job.dict())
    db_job.start_time = datetime.datetime.now()
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, job_id, job: schemas.JobUpdate):
    db_job = get_job(db, job_id)
    if db_job:
        for key, value in job.dict(exclude_unset=True).items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job


def update_job_2(job_id, status, error=None, db=None):
    if db:
        db_job = get_job(db, job_id)
        db_job.status = status
        db_job.comment = error
        if status == 'completed':
            db_job.end_time = datetime.datetime.now()
        if status == 'running':
            db_job.start_time = datetime.datetime.now()
            db_job.end_time = None
        db.commit()
    else:
        with get_db_2() as db:
            db_job = get_job(db, job_id)
            db_job.status = status
            db_job.comment = error
            if status == 'completed':
                db_job.end_time = datetime.datetime.now()
            if status == 'running':
                db_job.start_time = datetime.datetime.now()
            db.commit()
    return db_job


def delete_job(db: Session, job_id: int):
    db_job = get_job(db, job_id)
    if db_job:
        db.delete(db_job)
        db.commit()


# Task CRUD operations
def get_task(db: Session, task_id: int):
    return db.query(models.TaskDefinition).filter(models.TaskDefinition.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.TaskDefinition).offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskDefinitionCreate):
    db_task = models.TaskDefinition(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskDefinitionUpdate):
    db_task = get_task(db, task_id)
    if db_task:
        for key, value in task.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()


# Schedule CRUD operations
def get_schedule(db: Session, schedule_id: int):
    return db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()


def get_schedules(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Schedule).offset(skip).limit(limit).all()


def create_schedule(db: Session, schedule: schemas.ScheduleCreate):
    db_schedule = models.Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def update_schedule(db: Session, schedule_id: int, schedule: schemas.ScheduleUpdate):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule:
        for key, value in schedule.dict(exclude_unset=True).items():
            setattr(db_schedule, key, value)
        db.commit()
        db.refresh(db_schedule)
    return db_schedule


def delete_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule:
        db.delete(db_schedule)
        db.commit()


# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=user.password,  # You should hash the password here
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()


def update_row_model(row_model):
    session = SessionLocal()
    session.add(row_model)
    session.commit()
    session.close()
    return True
