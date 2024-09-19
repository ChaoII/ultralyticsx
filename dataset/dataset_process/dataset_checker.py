from pathlib import Path

from common.model_type_widget import ModelType
from .classify.classify_check_dataset import classify_dataset_check
from .detection.detection_check_dataset import detection_dataset_check


def check_dataset(dataset_path: Path, model_type: ModelType):
    if model_type == ModelType.CLASSIFY:
        return classify_dataset_check(dataset_path)
    if model_type == ModelType.DETECTION:
        return detection_dataset_check(dataset_path)
