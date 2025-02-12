from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship

from common.database.db_helper import Base, engine

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
    split_rate = Column(String, default="70_20_10")
    dataset_total = Column(Integer, default=0)
    tasks = relationship("TrainTask", back_populates="dataset")

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
    tasks = relationship("TrainTask", back_populates="project", cascade="all, delete")
    datasets = relationship("Dataset", secondary=projects_to_datasets, back_populates="projects")


class TrainTask(Base):
    __tablename__ = "tb_train_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String)
    project_id = Column(String, ForeignKey('tb_projects.project_id',ondelete="RESTRICT"))
    dataset_id = Column(String, ForeignKey("tb_datasets.dataset_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    elapsed = Column(String)
    task_status = Column(Integer, default=0)
    epoch = Column(Integer, default=0)
    epochs = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now())
    project = relationship("Project", back_populates="tasks")
    dataset = relationship("Dataset", back_populates="tasks")


class AnnotationTask(Base):
    __tablename__ = "tb_annotation_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String)
    task_name = Column(String)
    task_description = Column(String)
    model_type = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    elapsed = Column(String)
    task_status = Column(Integer, default=0)
    labeled_num = Column(Integer, default=0)
    total = Column(Integer, default=0)
    image_dir = Column(String)
    annotation_dir = Column(String)
    create_time = Column(DateTime, default=datetime.now())


Base.metadata.create_all(engine)
