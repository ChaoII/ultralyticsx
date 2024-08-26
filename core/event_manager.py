from PySide6.QtCore import QObject, Signal, Slot

from dataset.types import DatasetStatus


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

    def __init__(self):
        super().__init__()

    @Slot(str)
    def on_dataset_process_finished(self, dataset_config: str):
        self.dataset_process_finished.emit(dataset_config)

    @Slot(str, DatasetStatus)
    def on_import_dataset_finished(self, dataset_id: str, status: DatasetStatus):
        self.import_dataset_finished.emit(dataset_id, status)
