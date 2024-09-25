from pprint import pprint

from PySide6.QtCore import Signal, QThread

from ultralytics import YOLO
from ...types import TaskInfo


class ModelValThread(QThread):
    model_val_start = Signal(int)
    model_val_batch_end = Signal(int)
    model_val_end = Signal(list)
    model_val_failed = Signal(str)

    def __init__(self, val_parameters: dict):
        super().__init__()
        self._validator: YOLO | None = None
        self._val_parameters = val_parameters
        self._task_info: TaskInfo | None = None
        self._last_model = ""

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        pass

    def init_model_exporter(self) -> bool:
        try:
            self._validator = YOLO(self._val_parameters.pop("model_name"))
            self._validator.add_callback("on_val_start", self._on_val_start)
            self._validator.add_callback("on_val_batch_end", self._on_val_batch_end)
            self._validator.add_callback("on_val_end", self._on_val_end)
            return True
        except FileNotFoundError as e:
            error_msg = str(e)
            self.model_val_failed.emit(error_msg)
            return False

    def get_last_model(self):
        return self._last_model

    def _on_val_start(self, validator):
        total_batch = validator.batches
        self.model_val_start.emit(total_batch)

    def _on_val_batch_end(self, validator):
        cur_batch = validator.batch
        self.model_val_batch_end.emit(cur_batch)

    def _on_val_end(self, validator):
        self.model_val_end.emit(validator.get_val_results())

    def run(self):
        if self._validator:
            try:
                self._validator.val(workers=0, **self._val_parameters)
            except Exception as e:
                self.model_val_failed.emit(str(e))
