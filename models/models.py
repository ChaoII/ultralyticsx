from datetime import datetime

from common.db_helper import db_session
from common.db_helper import Base, engine
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String)
    project_id = Column(String)
    project_description = Column(String)
    project_type = Column(Integer)
    workspace_dir = Column(String)
    create_time = Column(DateTime, default=datetime.now())
    tasks = relationship("Task", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String)
    project_id = Column(String, ForeignKey('projects.project_id'))
    comment = Column(String)
    task_status = Column(Integer)
    create_time = Column(DateTime, default=datetime.now())
    project = relationship("Project", back_populates="tasks")


Base.metadata.create_all(engine)
