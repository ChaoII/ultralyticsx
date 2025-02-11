from common.database.db_helper import db_session
from models.models import AnnotationTask


def db_update_annotation_dir_path(annotation_task_id, annotation_dir_path: str):
    with db_session() as session:
        task: AnnotationTask = session.query(AnnotationTask).filter_by(task_id=annotation_task_id).first()
        task.annotation_dir = annotation_dir_path
