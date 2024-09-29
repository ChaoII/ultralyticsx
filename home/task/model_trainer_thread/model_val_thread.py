import pickle

from PySide6.QtCore import Signal, QThread

from common.database.task_helper import db_update_task_status
from ultralytics import YOLO
from ...types import TaskInfo, TaskStatus


class ModelValThread(QThread):
    model_val_start = Signal(int)
    model_val_batch_end = Signal(int)
    model_val_end = Signal(list, dict)
    model_val_failed = Signal(str)

    def __init__(self, val_parameters: dict):
        super().__init__()
        self._validator: YOLO | None = None
        self._val_parameters = val_parameters
        self._task_info: TaskInfo | None = None

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info

    def init_model_validator(self) -> bool:
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

    def _on_val_start(self, validator):
        total_batch = validator.batches
        self.model_val_start.emit(total_batch)

    def _on_val_batch_end(self, validator):
        cur_batch = validator.batch
        self.model_val_batch_end.emit(cur_batch)

    def _on_val_end(self, validator):
        val_result = validator.get_val_results()
        val_speed = validator.speed
        db_update_task_status(self._task_info.task_id, TaskStatus.VAL_FINISHED)
        with open(self._task_info.task_dir / "val_results.pkl", mode="wb") as f:
            pickle.dump([val_result, val_speed], f)
        self.model_val_end.emit(val_result, val_speed)

    def run(self):
        try:
            if not self.init_model_validator():
                return
            self._validator.val(workers=0, **self._val_parameters)
        except Exception as e:
            self.model_val_failed.emit(str(e))
