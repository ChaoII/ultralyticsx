import pandas as pd
import pickle

import ultralytics
from dataset.dataset_detail_widget.common.label_table_Widget import SplitLabelInfo
from dataset.types import DatasetType
from ultralytics import YOLO

# df_path = r"C:\Users\84945\Desktop\ultralytics_workspace\dataset\D000000\split_cache1"
#
# dataset_frame: pd.DataFrame = pickle.load(open(df_path, "rb"))
# dataset_frame.loc[dataset_frame["label"] == "bocai", "label"] = 0
# dataset_frame.loc[dataset_frame["label"] == "changqiezi", "label"] = 1
# dataset_frame.loc[dataset_frame["label"] == "hongxiancai", "label"] = 2
# dataset_frame.loc[dataset_frame["label"] == "huluobo", "label"] = 3
# dataset_frame.loc[dataset_frame["label"] == "xihongshi", "label"] = 4
# dataset_frame.loc[dataset_frame["label"] == "xilanhua", "label"] = 5
# df_mode: pd.DataFrame = dataset_frame[dataset_frame["type"] == "train"]
# simples = df_mode.loc[:, ["image_path", "label"]].to_records(index=False)
#
# pickle.dump(dataset_frame, open(df_path, "wb"))

# model = YOLO("yolov8n.pt")
# results = model.train(data="coco8.yaml", epochs=100, imgsz=640, device=0, workers=0)

# model.export(format="onnx")
# s = model.val(workers=0, save_dir="./", plots=False, split="test")
# print(s)

from collections import Counter


def load_split_info(dataset_df: pd.DataFrame) -> list[SplitLabelInfo]:
    all_num = dataset_df.shape[0]
    train_num = dataset_df.groupby("type").groups[DatasetType.TRAIN.value].size
    val_num = dataset_df.groupby("type").groups[DatasetType.VAL.value].size
    test_num = dataset_df.groupby("type").groups[DatasetType.TEST.value].size
    info = SplitLabelInfo(label="All images", all_num=all_num, train_num=train_num, val_num=val_num, test_num=test_num)

    dataset_split_num_info = [info]
    labels_map = dict()

    for key, group in dataset_df.groupby("type").groups.items():
        label_df = dataset_df.loc[group, "label_path"]
        labels = []
        for label_path in label_df:
            with open(label_path, "r", encoding="utf8") as f:
                data = f.readlines()
                for line in data:
                    label = line.split(" ")[0]
                    labels.append(label)
        labels_map[key] = Counter(labels)
    df_counter = pd.DataFrame(labels_map).sort_index()
    df_sum = df_counter.sum().to_frame().T.reset_index(names="label")
    df_sum["label"] = -1
    df_all = pd.concat([df_sum, df_counter.reset_index(names="label")], axis=0)

    for row in df_counter.iterrows():
        key, value = row
        label_num = value.sum()
        train_num = value[DatasetType.TRAIN.value]
        val_num = value[DatasetType.VAL.value]
        test_num = value[DatasetType.TEST.value]
        dataset_split_num_info.append(SplitLabelInfo(label=key,
                                                     all_num=label_num,
                                                     train_num=train_num,
                                                     val_num=val_num,
                                                     test_num=test_num
                                                     ))

    return dataset_split_num_info


df = pickle.load(open(r"C:\Users\84945\Desktop\ultralytics_workspace\dataset\D000002\split_cache", "rb"))

print(load_split_info(df))
