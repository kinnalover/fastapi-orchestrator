import uuid

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Common response model with id and timestamp fields
class OrmBase(BaseModel):
    id: Optional[Optional[int | uuid.UUID]]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

# Process schemas
class ProcessBase(BaseModel):
    name: str
    description: Optional[str]
    repository_url: Optional[str]
class ProcessCreate(ProcessBase):
    pass

class ProcessUpdate(ProcessBase):
    pass

class Process(OrmBase, ProcessBase):
    pass

# Machine schemas
class MachineBase(BaseModel):
    name: str
    ip_address: str
    status: Optional[str]

class MachineCreate(MachineBase):
    pass

class MachineUpdate(MachineBase):
    pass

class Machine(OrmBase, MachineBase):
    pass

# Job schemas
class JobBase(BaseModel):
    process_id: uuid.UUID
    machine_id: uuid.UUID
    status: Optional[str] = "pending"

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class Job(OrmBase, JobBase):
    pass

# Task schemas
class TaskDefinitionBase(BaseModel):
    name: str
    description: Optional[str]

class TaskDefinitionCreate(TaskDefinitionBase):
    pass

class TaskDefinitionUpdate(TaskDefinitionBase):
    pass

class TaskDefinition(OrmBase, TaskDefinitionBase):
    pass

# Schedule schemas
class ScheduleBase(BaseModel):
    task_id: int
    cron_expression: str
    enabled: bool = True

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    pass

class Schedule(OrmBase, ScheduleBase):
    pass

# User schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str]
    full_name: Optional[str]

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    pass

class User(OrmBase, UserBase):
    pass
