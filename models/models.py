from datetime import datetime
from typing import List

from common.db_helper import db_session
from common.db_helper import Base, engine
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Mapped

projects_to_datasets = Table(
    "projects_to_datasets",
    Base.metadata,
    Column("project_id", ForeignKey("tb_projects.id")),
    Column("dataset_id", ForeignKey("tb_datasets.id")),
)


class Dataset(Base):
    __tablename__ = "tb_datasets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String)
    dataset_name = Column(String)
    model_type = Column(Integer)
    dataset_description = Column(String)
    dataset_status = Column(Integer)
    dataset_dir = Column(String)
    create_time = Column(DateTime, default=datetime.now())

    projects = relationship("Project", secondary=projects_to_datasets, back_populates="datasets")


class Project(Base):
    __tablename__ = 'tb_projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String)
    project_id = Column(String)
    project_description = Column(String)
    model_type = Column(Integer)
    project_dir = Column(String)
    create_time = Column(DateTime, default=datetime.now())

    tasks = relationship("Task", back_populates="project")

    datasets = relationship("Dataset", secondary=projects_to_datasets, back_populates="projects")


class Task(Base):
    __tablename__ = "tb_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String)
    project_id = Column(String, ForeignKey('tb_projects.project_id'))
    comment = Column(String)
    task_status = Column(Integer)
    create_time = Column(DateTime, default=datetime.now())
    project = relationship("Project", back_populates="tasks")


Base.metadata.create_all(engine)
