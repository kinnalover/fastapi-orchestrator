from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Schedule)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    return crud.create_schedule(db=db, schedule=schedule)

@router.get("/{schedule_id}", response_model=schemas.Schedule)
def get_schedule(schedule_id: str, db: Session = Depends(get_db)):
    db_schedule = crud.get_schedule(db, schedule_id=schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.get("/", response_model=list[schemas.Schedule])
def list_schedules(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_schedules(db, skip=skip, limit=limit)

@router.put("/{schedule_id}", response_model=schemas.Schedule)
def update_schedule(schedule_id: str, schedule: schemas.ScheduleUpdate, db: Session = Depends(get_db)):
    return crud.update_schedule(db, schedule_id=schedule_id, schedule=schedule)

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: str, db: Session = Depends(get_db)):
    crud.delete_schedule(db, schedule_id=schedule_id)
    return {"detail": "Schedule deleted"}
