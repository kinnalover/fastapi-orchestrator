import uuid

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Job)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    print(f"create a job {job.__dict__}")
    return crud.create_job(db=db, job=job)

@router.get("/{job_id}", response_model=schemas.Job)
def get_job(job_id: str, db: Session = Depends(get_db)):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.get("/by/{process_id}", response_model=schemas.Job)
def get_job_by_process_id(process_id: uuid.UUID, db: Session = Depends(get_db)):
    db_job = crud.get_job_by_process_id(db, process_id=process_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return db_job

@router.get("/", response_model=list[schemas.Job])
def list_jobs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_jobs(db, skip=skip, limit=limit)

@router.put("/{job_id}", response_model=schemas.Job)
def update_job(job_id: str, job: schemas.JobUpdate, db: Session = Depends(get_db)):
    return crud.update_job(db, job_id=job_id, job=job)

@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    crud.delete_job(db, job_id=job_id)
    return {"detail": "Job deleted"}
