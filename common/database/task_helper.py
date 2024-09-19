from common.database.db_helper import db_session
from models.models import Task


def update_task_epoch_info(task_id, epoch, epochs):
    with db_session() as session:
        task = session.query(Task).filter_by(task_id=task_id).first()
        task.epoch = epoch
        task.epochs = epochs
