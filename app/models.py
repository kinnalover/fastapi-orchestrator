from sqlalchemy import Column, String, Text, Enum, ForeignKey, DateTime, create_engine, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm
from app import config

Base = declarative_base()


class Process(Base):
    __tablename__ = 'processes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repository_url = Column(String(255))
    folderPath = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    default_machine = Column(Text)
    default_machines = Column(Text)
    tasks = relationship('TaskDefinition', back_populates='process')


class Machine(Base):
    __tablename__ = 'machines'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    status = Column(Enum('online', 'offline', 'busy', 'disconnected', name='machine_status'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    last_heartbeat = Column(DateTime)

    jobs = relationship('Job', back_populates='machine')
    heartbeats = relationship('AgentHeartbeat', back_populates='machine')


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey('processes.id'), nullable=False)
    machine_id = Column(UUID(as_uuid=True), ForeignKey('machines.id'), nullable=False)
    status = Column(Enum('pending', 'running', 'completed', 'failed', name='job_status'), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    log = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    comment = Column(Text)
    machine = relationship('Machine', back_populates='jobs')
    process = relationship('Process')
    task_executions = relationship('TaskExecution', back_populates='job')


class TaskDefinition(Base):
    __tablename__ = 'task_definitions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey('processes.id'), nullable=False)
    name = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)
    type = Column(Enum('celery', 'http', 'script', name='task_type'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    process = relationship('Process', back_populates='tasks')
    task_executions = relationship('TaskExecution', back_populates='task')


class TaskExecution(Base):
    __tablename__ = 'task_executions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey('task_definitions.id'), nullable=False)
    status = Column(Enum('pending', 'running', 'completed', 'failed', name='task_execution_status'), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    log = Column(Text)

    job = relationship('Job', back_populates='task_executions')
    task = relationship('TaskDefinition', back_populates='task_executions')


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'developer', 'viewer', name='user_role'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

class MachineProcessMapping(Base):
    __tablename__ = 'machine_process_mappings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey('machines.id'), nullable=False)
    process_id = Column(UUID(as_uuid=True), ForeignKey('processes.id'), nullable=False)

    machine = relationship('Machine')
    process = relationship('Process')


class AgentTask(Base):
    __tablename__ = 'agent_tasks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('task_definitions.id'), nullable=False)
    status = Column(Enum('pending', 'running', 'completed', 'failed', name='agent_task_status'), nullable=False)
    result = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    task = relationship('TaskDefinition')


class AgentHeartbeat(Base):
    __tablename__ = 'agent_heartbeats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey('machines.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now())
    status = Column(Enum('healthy', 'degraded', 'unhealthy', name='agent_heartbeat_status'), nullable=False)

    machine = relationship('Machine', back_populates='heartbeats')


# Replace the connection string with your database configuration

class Trigger(Base):
    __tablename__ = "triggers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=True)
    process_id = Column(UUID(as_uuid=True), ForeignKey('processes.id'), nullable=False)
    machine_id = Column(UUID(as_uuid=True), ForeignKey('machines.id'), nullable=False)
    schedule_type =  Column(String, nullable=False)
    selected_days =Column(String, nullable=True)
    schedule_time = Column(String, nullable=False)
    celery_task_id = Column(String, nullable=True)  # Store Celery task ID
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

engine = create_engine(config.SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

class RPALog(Base):
    __tablename__ = 'rpa_log'
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    asctime: orm.Mapped[datetime]
    filename: orm.Mapped[str]
    funcname: orm.Mapped[str]
    levelname: orm.Mapped[str]
    lineno: orm.Mapped[int]
    message: orm.Mapped[str]
    module: orm.Mapped[str]
    name: orm.Mapped[str]
    pathname: orm.Mapped[str]
    process: orm.Mapped[str]
    processname: orm.Mapped[str]
    thread: orm.Mapped[int]
    threadname: orm.Mapped[str]