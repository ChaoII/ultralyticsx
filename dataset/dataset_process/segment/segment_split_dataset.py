from pathlib import Path

from ..detection.detection_split_dataset import detection_dataset_split


def segment_dataset_split(dataset_dir: Path | str, split_rates: list):
    return detection_dataset_split(dataset_dir, split_rates)
