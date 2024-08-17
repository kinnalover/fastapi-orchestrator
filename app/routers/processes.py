from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Process)
def create_process(process: schemas.ProcessCreate, db: Session = Depends(get_db)):
    return crud.create_process(db=db, process=process)


@router.get("/{process_id}", response_model=schemas.Process)
def get_process(process_id: str, db: Session = Depends(get_db)):
    print("geting process_id", process_id)
    try:
        db_process = crud.get_process(db, process_id=process_id)
    except Exception as e:
        db_process = None
        print('d')
    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    return db_process


@router.get("/", response_model=list[schemas.Process])
def list_processes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_processes(db, skip=skip, limit=limit)


@router.put("/{process_id}", response_model=schemas.Process)
def update_process(process_id: str, process: schemas.ProcessUpdate, db: Session = Depends(get_db)):
    return crud.update_process(db, process_id=process_id, process=process)


@router.delete("/{process_id}")
def delete_process(process_id: str, db: Session = Depends(get_db)):
    crud.delete_process(db, process_id=process_id)
    return {"detail": "Process deleted"}
