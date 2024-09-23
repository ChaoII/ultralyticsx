from pathlib import Path

from common.model_type_widget import ModelType
from dataset.dataset_process.classify.classify_split_dataset import classify_dataset_split
from dataset.dataset_process.detection.detection_split_dataset import detection_dataset_split
from dataset.dataset_process.pose.pose_split_dataset import pose_dataset_split
from dataset.dataset_process.segment.segment_split_dataset import segment_dataset_split


def split_dataset(dataset_dir: Path, split_rates: list, model_type: ModelType):
    if model_type == ModelType.CLASSIFY:
        return classify_dataset_split(dataset_dir, split_rates)
    elif model_type == ModelType.DETECT:
        return detection_dataset_split(dataset_dir, split_rates)
    elif model_type == ModelType.SEGMENT:
        return segment_dataset_split(dataset_dir, split_rates)
    elif model_type == ModelType.POSE:
        return pose_dataset_split(dataset_dir, split_rates)
    else:
        raise ValueError("model type not support")
