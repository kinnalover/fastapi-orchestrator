from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.TaskDefinition)
def create_task(task: schemas.TaskDefinitionCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

@router.get("/{task_id}", response_model=schemas.TaskDefinition)
def get_task(task_id: str, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.get("/", response_model=list[schemas.TaskDefinition])
def list_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit)

@router.put("/{task_id}", response_model=schemas.TaskDefinition)
def update_task(task_id: str, task: schemas.TaskDefinitionUpdate, db: Session = Depends(get_db)):
    return crud.update_task(db, task_id=task_id, task=task)

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id=task_id)
    return {"detail": "Task deleted"}
