from PySide6.QtCore import QObject, Signal, Slot


class EventManager(QObject):
    _instance = None

    @staticmethod
    def get_instance():
        if EventManager._instance is None:
            EventManager._instance = EventManager()
        return EventManager._instance

    dataset_process_finished = Signal(str)

    def __init__(self):
        # 实际上我们不想在这里创建多个实例，但 QObject 需要调用基类构造函数
        if EventManager._instance is not None:
            raise Exception("Use get_instance() to get the single instance of this class.")
        super(EventManager, self).__init__()

    @Slot(str)
    def on_dataset_process_finished(self, dataset_config: str):
        self.dataset_process_finished.emit(dataset_config)
