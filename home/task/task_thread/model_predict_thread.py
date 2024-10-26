from pathlib import Path

from PySide6.QtCore import Signal, QThread
from PySide6.QtGui import QImage

from common.utils.draw_labels import draw_detect_result, draw_segment_result, draw_obb_result, draw_pose_result, \
    draw_classify_result
from common.component.model_type_widget import ModelType
from ultralytics import YOLO
from ultralytics.engine.results import Results
from ...types import TrainTaskInfo


class ModelPredictorThread(QThread):
    model_predict_end = Signal(QImage, Results)
    model_predict_failed = Signal(str)

    def __init__(self, model_path: Path):
        super().__init__()
        self._predictor: YOLO | None = None
        self._model_path = model_path
        self._task_info: TrainTaskInfo | None = None
        self._image_path: Path | None = None

    def set_task_info(self, task_info: TrainTaskInfo):
        self._task_info = task_info

    def set_predict_image(self, image_path: Path):
        self._image_path = image_path

    def draw_image(self, result: Results) -> QImage:
        pix = QImage(self._image_path)
        if self._task_info.model_type == ModelType.CLASSIFY:
            label = result.names[result.probs.top1]
            draw_classify_result(pix, label)
        if self._task_info.model_type == ModelType.DETECT:
            draw_detect_result(pix, result.names, result.boxes.data.cpu().tolist())
        if self._task_info.model_type == ModelType.SEGMENT:
            draw_segment_result(pix, result.names, result.boxes.data.cpu().tolist(), result.masks.xy)
        if self._task_info.model_type == ModelType.OBB:
            draw_obb_result(pix, result.names, result.obb.cls.cpu().tolist(), result.obb.conf.cpu().tolist(),
                            result.obb.xyxyxyxy.cpu().tolist())
        if self._task_info.model_type == ModelType.POSE:
            draw_pose_result(pix, result.names, result.boxes.data.cpu().tolist(), result.keypoints.data.cpu().tolist())
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
                self.model_predict_end.emit(image, results[0])
            except Exception as e:
                self.model_predict_failed.emit(str(e))
