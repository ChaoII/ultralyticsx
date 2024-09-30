from PySide6.QtCore import QObject, Signal

from dataset.types import DatasetStatus
from home.types import TaskStatus


class SignalBridge(QObject):
    dataset_process_finished = Signal(str)
    import_dataset_finished = Signal(str, DatasetStatus)
    train_status_changed = Signal(str, int, int, str, str, str, TaskStatus)


signal_bridge = SignalBridge()
