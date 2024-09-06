import pickle
import random
import shutil
from pathlib import Path
import pandas as pd

from dataset.types import DatasetType


class ClassifySplitDataset:
    label: list[str]
    train_dataset: list[list[str, int]]
    val_dataset: list[list[str, int]]
    test_dataset: list[list[str, int]]

    def __init__(self, label: list[str], train_dataset, val_dataset, test_dataset):
        self.label = label
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset


def load_split_dataset(dataset_dir: Path):
    dataset_df = pickle.load(open(dataset_dir / "split_cache", "rb"))
    return dataset_df


def split_dataset(dataset_dir: Path, split_rates: list):
    dataset_map = dict()
    label_list = []
    for item in dataset_dir.iterdir():
        if item.is_dir():
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
        cur_label_val_data = [[item[index], key] for index in label_dataset_index[train_num:train_num + val_num]]
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
    for key, group in all_df.groupby(["type", "label"]).groups.items():
        dir = dataset_dir / "split" / key[0] / key[1]
        dir.mkdir(parents=True, exist_ok=True)
        file_names = all_df.loc[group, "image_path"]
        for file_name in file_names:
            shutil.move(file_name, dir)
    pickle.dump(all_df, open(dataset_dir / "split_cache", "wb"))
    return all_df


if __name__ == '__main__':
    # split_dataset(Path(r"C:\Users\AC\Desktop\1231\dataset\D000000"), [70, 20, 10])
    split_dataset(Path(r"C:\Users\AC\Desktop\1231\dataset\D000001"))
