from pathlib import Path

from PySide6.QtCore import Signal, QThread
from ultralytics import YOLO
from ...types import TaskInfo


class ModelPredictorThread(QThread):
    model_predict_end = Signal(list)
    model_predict_failed = Signal(str)

    def __init__(self, model_path: Path):
        super().__init__()
        self._predictor: YOLO | None = None
        self._model_path = model_path
        self._task_info: TaskInfo | None = None
        self._image_path: Path | None = None

    def set_predict_image(self, image_path: Path):
        self._image_path = image_path

    def run(self):
        try:
            self._predictor = YOLO(self._model_path)
        except FileNotFoundError as e:
            error_msg = str(e)
            self.model_predict_failed.emit(error_msg)
            return
        if self._predictor and self._image_path:
            try:
                results = self._predictor.predict(self._image_path)
                self.model_predict_end.emit(results)
            except Exception as e:
                self.model_predict_failed.emit(str(e))
