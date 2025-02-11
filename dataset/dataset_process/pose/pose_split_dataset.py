from pathlib import Path

from ..utils import coco_dataset_split, save_coco_pose_yaml


def pose_dataset_split(dataset_dir: Path | str, split_rates: list):
    all_df, dst_dir = coco_dataset_split(dataset_dir, split_rates)
    save_coco_pose_yaml(dataset_dir, dst_dir)
    return all_df
