import pickle
import random
import shutil
from pathlib import Path
from loguru import logger
import pandas as pd
import yaml

from common.utils.utils import is_empty, is_image


def load_split_dataset(dataset_dir: Path):
    dataset_df = pickle.load(open(dataset_dir / "split_cache", "rb"))
    return dataset_df


def classify_dataset_check(dataset_dir: Path | str):
    exist_one_type = False
    if is_empty(dataset_dir):
        return False
    for item in dataset_dir.iterdir():
        if item.is_dir():
            exist_one_type = True
            if is_empty(item):
                return False
            for file in item.iterdir():
                if file.is_file():
                    if not is_image(file):
                        return False
                else:
                    return False
        else:
            continue
    return exist_one_type


def coco_dataset_check(dataset_dir: Path | str):
    if isinstance(dataset_dir, str):
        dataset_dir = Path(dataset_dir)

    if not dataset_dir.is_dir():
        logger.error("输入路径不是一个有效的目录")
        return False

    # 检查文件夹是否包含images和labels和classes.txt
    images_path = dataset_dir / "images"
    labels_path = dataset_dir / "labels"
    classes_file_path = dataset_dir / "classes.txt"
    if not images_path.exists():
        logger.error("源数据集未包含[images]目录")
        return False
    if not labels_path.exists():
        logger.error("源数据集未包含[labels]目录")
        return False
    if not classes_file_path.exists():
        logger.error("数据集中未包含[classes.txt]文件")
        return False

    if is_empty(images_path):
        logger.error("[images]目录为空")
        return False

    if is_empty(labels_path):
        logger.error("[labels]目录为空")
        return False

    labels = []
    for item in labels_path.iterdir():
        if not item.is_file() or item.suffix != ".txt":
            logger.error(f"源数据集[labels]路径中，存在非txt文件或路径{item.name}")
            return False
        labels.append(item.stem)
    for item in images_path.iterdir():
        if not item.is_file() or not is_image(item):
            logger.error(f"源数据集[images]路径中，存在非图片的文件或路径{item.name}")
            return False
        if item.stem not in labels:
            logger.error(f"labels目录下没有对应的label，{item.name}")
            return False
    return True


def classify_dataset_split(dataset_dir: Path | str, split_rates: list | tuple) -> pd.DataFrame | None:
    if isinstance(dataset_dir, str):
        dataset_dir = Path(dataset_dir)

    dataset_map = dict()
    label_list = []
    for item in (dataset_dir / "src").iterdir():
        if item.is_dir():
            if item.name == "split":
                continue
            images = list(map(lambda x: x.resolve().as_posix(), item.iterdir()))
            dataset_map[item.name] = images
            label_list.append(item.name)

    train_dataset_list = []
    val_dataset_list = []
    test_dataset_list = []

    for key, item in dataset_map.items():
        label_dataset_num = len(item)
        train_num = round(label_dataset_num * split_rates[0] / 100)
        val_num = round(label_dataset_num * split_rates[1] / 100)
        test_num = label_dataset_num - train_num - val_num
        label_dataset_index = list(range(len(item)))
        random.shuffle(label_dataset_index)
        cur_label_train_data = [[item[index], key] for index in label_dataset_index[:train_num]]
        cur_label_val_data = [[item[index], key] for index in
                              label_dataset_index[train_num:train_num + val_num]]
        cur_label_test_data = [[item[index], key] for index in label_dataset_index[train_num + val_num:]]
        train_dataset_list.extend(cur_label_train_data)
        val_dataset_list.extend(cur_label_val_data)
        test_dataset_list.extend(cur_label_test_data)

    train_df = pd.DataFrame(train_dataset_list, index=None, columns=['image_path', 'label'])
    train_df["type"] = ["train"] * len(train_dataset_list)
    val_df = pd.DataFrame(val_dataset_list, index=None, columns=['image_path', 'label'])
    val_df["type"] = ["val"] * len(val_dataset_list)
    test_df = pd.DataFrame(test_dataset_list, index=None, columns=['image_path', 'label'])
    test_df["type"] = ["test"] * len(test_dataset_list)
    all_df = pd.concat([train_df, val_df, test_df]).reset_index(drop=True)
    dst_dir = dataset_dir / "split"
    if dst_dir.exists():
        shutil.rmtree(dst_dir)

    for key, group in all_df.groupby(["type", "label"]).groups.items():
        split_dir = dst_dir / key[0] / key[1]
        split_dir.mkdir(parents=True, exist_ok=True)
        for index in group:
            filename = all_df.loc[index, "image_path"]
            all_df.loc[index, "image_path"] = (split_dir / Path(filename).name).resolve().as_posix()
            shutil.copy(filename, split_dir)
    pickle.dump(all_df, open(dataset_dir / "split_cache", "wb"))
    return all_df


def coco_dataset_split(dataset_dir: Path | str, split_rates: list, is_pose: bool = False) -> pd.DataFrame | None:
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
    if train_num == 0 or val_num == 0:
        return None
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
    save_config_yaml(dataset_dir, dst_dir, is_pose)
    return all_df


def save_config_yaml(dataset_dir: Path, dst_dir: Path, is_pose: bool = False):
    dst_yaml_path = dst_dir / "config.yaml"
    dataset_config = dict()
    with open(dst_yaml_path, 'w', encoding="utf8") as file:
        dataset_config.update({"path": dst_dir.resolve().as_posix()})
        dataset_config.update({"train": "images/train"})
        dataset_config.update({"val": "images/val"})
        dataset_config.update({"test": "images/test"})
        if is_pose:
            dataset_config.update({"kpt_shape": [17, 3],
                                   "flip_idx": [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]})
            dataset_config.update({"names": {0: "person"}})
        else:
            with open(dataset_dir / "src" / "classes.txt", "r", encoding="utf8") as f:
                labels = [line.strip() for line in f.readlines()]
            labels_map = {index: label for index, label in enumerate(labels)}
            dataset_config.update({"names": labels_map})
        yaml.dump(dataset_config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
