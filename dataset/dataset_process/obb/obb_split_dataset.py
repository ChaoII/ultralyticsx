from pathlib import Path

from dataset.dataset_process.utils import save_coco_detect_and_segment_yaml, coco_dataset_split


def obb_dataset_split(dataset_dir: Path | str, split_rates: list):
    all_df, dst_dir = coco_dataset_split(dataset_dir, split_rates)
    save_coco_detect_and_segment_yaml(dataset_dir, dst_dir)
    return all_df


if __name__ == '__main__':
    # split_dataset(Path(r"C:\Users\AC\Desktop\1231\dataset\D000000"), [70, 20, 10])
    obb_dataset_split(Path(r"C:\Users\84945\Desktop\ultralytics_workspace\dataset\D000002"), [70, 20, 10])
