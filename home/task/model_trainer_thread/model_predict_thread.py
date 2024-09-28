from pathlib import Path

from PySide6.QtCore import Signal, QThread
from PySide6.QtGui import QPainter, QImage

from common.model_type_widget import ModelType
from common.utils import draw_classify, generate_random_color
from ultralytics.engine.results import Results

from ultralytics import YOLO
from ...types import TaskInfo


class ModelPredictorThread(QThread):
    model_predict_end = Signal(QImage, list)
    model_predict_failed = Signal(str)

    def __init__(self, model_path: Path):
        super().__init__()
        self._predictor: YOLO | None = None
        self._model_path = model_path
        self._task_info: TaskInfo | None = None
        self._image_path: Path | None = None

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info

    def set_predict_image(self, image_path: Path):
        self._image_path = image_path

    def draw_image(self, results: Results) -> QImage:
        if self._task_info.model_type == ModelType.CLASSIFY:
            painter = QPainter()
            pix = QImage(self._image_path)
            label = results.names[results.probs.top1]
            color = generate_random_color()
            draw_classify(painter, pix, label, color)
            return pix

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
                image = self.draw_image(results[0])
                self.model_predict_end.emit(image, results)
            except Exception as e:
                self.model_predict_failed.emit(str(e))
