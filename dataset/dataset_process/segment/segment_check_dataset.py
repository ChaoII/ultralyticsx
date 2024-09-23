from pathlib import Path

from ..detection.detection_check_dataset import detection_dataset_check


def segment_dataset_check(dataset_dir: Path | str):
    return detection_dataset_check(dataset_dir)
