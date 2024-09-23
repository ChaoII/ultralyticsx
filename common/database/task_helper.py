from datetime import datetime

from common.database.db_helper import db_session
from home.types import TaskStatus
from models.models import Task


def db_update_task_epoch_info(task_id, epoch, epochs):
    with db_session() as session:
        task = session.query(Task).filter_by(task_id=task_id).first()
        task.epoch = epoch
        task.epochs = epochs


def db_update_task_pause(task_id):
    with db_session() as session:
        task = session.query(Task).filter_by(task_id=task_id).first()
        task.task_status = TaskStatus.TRN_PAUSE.value


def db_update_task_finished(task_id, end_time: datetime, elapsed: str):
    with db_session() as session:
        task: Task = session.query(Task).filter_by(task_id=task_id).first()
        task.task_status = TaskStatus.TRN_FINISHED.value
        task.end_time = end_time
        task.elapsed = elapsed


def db_update_task_started(task_id, start_time: datetime):
    with db_session() as session:
        task: Task = session.query(Task).filter_by(task_id=task_id).first()
        task.task_status = TaskStatus.TRAINING.value
        task.start_time = start_time
        task.end_time = None
        task.elapsed = None


def db_update_task_failed(task_id):
    with db_session() as session:
        task: Task = session.query(Task).filter_by(task_id=task_id).first()
        task.task_status = TaskStatus.TRAIN_FAILED.value
        task.end_time = None
        task.elapsed = None


def db_get_project_id(task_id: str) -> str:
    with db_session() as session:
        task: Task = session.query(Task).filter_by(task_id=task_id).first()
        return task.project_id
