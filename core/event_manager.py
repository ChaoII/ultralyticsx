from PySide6.QtCore import QObject, Signal, Slot

from dataset.types import DatasetStatus
from home.types import TaskStatus


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class EventManager(QObject):
    dataset_process_finished = Signal(str)
    import_dataset_finished = Signal(str, DatasetStatus)

    train_status_changed = Signal(str, int, int, TaskStatus)

    def __init__(self):
        super().__init__()
