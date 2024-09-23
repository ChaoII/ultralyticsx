from pathlib import Path

from common.model_type_widget import ModelType
from dataset.dataset_process.classify.classify_check_dataset import classify_dataset_check
from dataset.dataset_process.detection.detection_check_dataset import detection_dataset_check
from dataset.dataset_process.segment.segment_check_dataset import segment_dataset_check


def check_dataset(dataset_path: Path, model_type: ModelType):
    if model_type == ModelType.CLASSIFY:
        return classify_dataset_check(dataset_path)
    if model_type == ModelType.DETECT:
        return detection_dataset_check(dataset_path)
    if model_type == ModelType.SEGMENT:
        return segment_dataset_check(dataset_path)
