from celery import Celery

celery_app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//', backend='rpc://')
from app.database import SessionLocal
from app.models import Job
@celery_app.task()
def run_process( process_id, machine_id):
    print(f"Starting job {process_id} on machine {machine_id}")

    executed_task = Job(
        process_id=process_id,
        machine_id=machine_id,

        status='running',
    )
    db = SessionLocal()
    db.add(executed_task)
    db.commit()
    print("added job")
    # Store the executed task in the database

    print(f"Task  executed for process {process_id} on machine {machine_id}")
    return f"Task  executed"


if __name__ == '__main__':
    scheduled_tasks = celery_app.conf.beat_schedule
    print(f"scheduled tasks: {scheduled_tasks}")
    for task_name, task_info in scheduled_tasks.items():
        print(f"Task Name: {task_name}")
        print(f"Task Info: {task_info}")