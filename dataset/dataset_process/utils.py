import pickle
import random
import shutil
from pathlib import Path

import pandas as pd
import yaml


def coco_dataset_split(dataset_dir: Path | str, split_rates: list) -> (pd.DataFrame | None, str | None):
    if isinstance(dataset_dir, str):
        dataset_dir = Path(dataset_dir)
    # ./scr/images/xxx.jpg
    images_paths = list((dataset_dir / "src" / "images").iterdir())
    # labels_paths = list((dataset_dir / "src" / "labels").iterdir())
    # ./src/labels/xxx.txt
    labels_paths = [x.parent.parent / "labels" / (x.stem + ".txt") for x in images_paths]

    dataset_num = len(images_paths)
    train_num = round(dataset_num * split_rates[0] / 100)
    val_num = round(dataset_num * split_rates[1] / 100)
    test_num = dataset_num - train_num - val_num
    if train_num == 0 or val_num == 0:
        return None, None

    dataset_index = list(range(dataset_num))
    random.shuffle(dataset_index)

    train_data_list = [images_paths[index] for index in dataset_index[:train_num]]
    val_data_list = [images_paths[index] for index in dataset_index[train_num:train_num + val_num]]
    test_data_list = [images_paths[index] for index in dataset_index[train_num + val_num:]]

    train_label_list = [labels_paths[index] for index in dataset_index[:train_num]]
    val_label_list = [labels_paths[index] for index in dataset_index[train_num:train_num + val_num]]
    test_label_list = [labels_paths[index] for index in dataset_index[train_num + val_num:]]

    train_df = pd.DataFrame({"image_path": train_data_list, "label_path": train_label_list}, index=None)
    train_df["type"] = ["train"] * len(train_data_list)
    val_df = pd.DataFrame({"image_path": val_data_list, "label_path": val_label_list}, index=None)
    val_df["type"] = ["val"] * len(val_data_list)
    test_df = pd.DataFrame({"image_path": test_data_list, "label_path": test_label_list}, index=None)
    test_df["type"] = ["test"] * len(test_data_list)
    all_df = pd.concat([train_df, val_df, test_df]).reset_index(drop=True)

    dst_dir = dataset_dir / "split"
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    for key, group in all_df.groupby("type").groups.items():
        split_images_dir = dst_dir / "images" / str(key)
        split_labels_dir = dst_dir / "labels" / str(key)
        split_images_dir.mkdir(parents=True, exist_ok=True)
        split_labels_dir.mkdir(parents=True, exist_ok=True)
        for index in group:
            image_path = all_df.loc[index, "image_path"]
            label_path = all_df.loc[index, "label_path"]
            all_df.loc[index, "image_path"] = (split_images_dir / Path(image_path).name).resolve().as_posix()
            all_df.loc[index, "label_path"] = (split_labels_dir / Path(label_path).name).resolve().as_posix()
            shutil.copy(image_path, split_images_dir)
            shutil.copy(label_path, split_labels_dir)
    pickle.dump(all_df, open(dataset_dir / "split_cache", "wb"))
    return all_df, dst_dir


def save_coco_detect_and_segment_yaml(dataset_dir: Path, dst_dir: Path):
    with open(dataset_dir / "src" / "classes.txt", "r", encoding="utf8") as f:
        labels = [line.strip() for line in f.readlines()]
    labels_map = {index: label for index, label in enumerate(labels)}
    dst_yaml_path = dst_dir / "coco_cpy.yaml"
    dataset_config = dict()
    with open(dst_yaml_path, 'w', encoding="utf8") as file:
        dataset_config.update({"path": dst_dir.resolve().as_posix()})
        dataset_config.update({"train": "images/train"})
        dataset_config.update({"val": "images/val"})
        dataset_config.update({"test": "images/test"})
        dataset_config.update({"names": labels_map})
        yaml.dump(dataset_config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)


def save_coco_pose_yaml(dataset_dir: Path, dst_dir: Path):
    dst_yaml_path = dst_dir / "coco_cpy.yaml"
    dataset_config = dict()
    with open(dst_yaml_path, 'w', encoding="utf8") as file:
        dataset_config.update({"path": dst_dir.resolve().as_posix()})
        dataset_config.update({"train": "images/train"})
        dataset_config.update({"val": "images/val"})
        dataset_config.update({"test": "images/test"})
        dataset_config.update({"kpt_shape": [17, 3],
                               "flip_idx": [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]})
        dataset_config.update({"names": {0: "person"}})
        yaml.dump(dataset_config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
