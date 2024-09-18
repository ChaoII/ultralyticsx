from PySide6.QtCore import Slot, Signal, QThread, QObject
from loguru import logger
from home.types import TaskInfo, TaskStatus
from ultralytics import YOLO


class ModelExportThread(QThread):
    model_export_start = Signal()
    model_export_end = Signal()
    model_export_failed = Signal(str)

    def __init__(self, export_parameters: dict):
        super().__init__()
        self._exporter: YOLO | None = None
        self._export_parameters = export_parameters
        self._task_info: TaskInfo | None = None
        self._last_model = ""

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        pass

    def init_model_exporter(self) -> bool:
        try:
            self._exporter = YOLO(self._export_parameters.pop("model_name"))
            self._exporter.add_callback("on_export_start", self._on_export_start)
            self._exporter.add_callback("on_export_end", self._on_export_end)
            return True
        except FileNotFoundError as e:
            error_msg = str(e)
            self.model_export_failed.emit(error_msg)
            return False

    def get_last_model(self):
        return self._last_model

    def _on_export_start(self, exporter):
        self.model_export_start.emit()

    def _on_export_end(self, exporter):
        self.model_export_end.emit()

    def run(self):
        if self._exporter:
            try:
                self._exporter.export(**self._export_parameters)
            except Exception as e:
                self.model_export_failed.emit(str(e))
