import pickle
import random
import shutil
from pathlib import Path
import pandas as pd


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


def classify_dataset_split(dataset_dir: Path, split_rates: list):
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


if __name__ == '__main__':
    # split_dataset(Path(r"C:\Users\AC\Desktop\1231\dataset\D000000"), [70, 20, 10])
    split_dataset(Path(r"C:\Users\84945\Desktop\ultralytics_workspace\dataset\D000000"), [70, 20, 10])
