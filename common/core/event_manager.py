from PySide6.QtCore import QObject, Signal


class SignalBridge(QObject):
    dataset_process_finished = Signal(str)
    import_dataset_finished = Signal(str, int)
    train_status_changed = Signal(str, int, int, str, str, str, int)


signal_bridge = SignalBridge()
