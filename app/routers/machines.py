from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Machine)
def create_machine(machine: schemas.MachineCreate, db: Session = Depends(get_db)):
    return crud.create_machine(db=db, machine=machine)

@router.get("/{machine_id}", response_model=schemas.Machine)
def get_machine(machine_id: str, db: Session = Depends(get_db)):
    print(f"the /machine_id {machine_id}")
    db_machine = crud.get_machine(db, machine_id=machine_id)
    if db_machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return db_machine

@router.get("/", response_model=list[schemas.Machine])
def list_machines(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_machines(db, skip=skip, limit=limit)

@router.put("/{machine_id}", response_model=schemas.Machine)
def update_machine(machine_id: str, machine: schemas.MachineUpdate, db: Session = Depends(get_db)):
    return crud.update_machine(db, machine_id=machine_id, machine=machine)

@router.delete("/{machine_id}")
def delete_machine(machine_id: str, db: Session = Depends(get_db)):
    crud.delete_machine(db, machine_id=machine_id)
    return {"detail": "Machine deleted"}
