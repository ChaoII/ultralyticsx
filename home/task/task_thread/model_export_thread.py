from PySide6.QtCore import Signal, QThread

from ultralytics import YOLO
from ...types import TaskInfo


class ModelExportThread(QThread):
    model_export_start = Signal()
    model_export_end = Signal()
    model_export_failed = Signal(str)

    def __init__(self, export_parameters: dict):
        super().__init__()
        self._exporter: YOLO | None = None
        self._export_parameters = export_parameters
        # self._task_info: TaskInfo | None = None

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

    def _on_export_start(self, exporter):
        self.model_export_start.emit()

    def _on_export_end(self, exporter):
        self.model_export_end.emit()

    def run(self):
        try:
            if not self.init_model_exporter():
                return
            self._exporter.export(**self._export_parameters)
        except Exception as e:
            self.model_export_failed.emit(str(e))
