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

model = YOLO("yolov8n-obb.pt")
results = model.train(data="dota8.yaml", epochs=100, imgsz=640, device=0, workers=0)
# model.export(format="onnx")
# s = model.val(workers=0, save_dir="./", plots=False, split="test")
# print(s)

# with open(r"C:\Users\AC\Desktop\1231\dataset\coco8-pose\labels\000000000049.txt", "r", encoding="utf8") as f:
#     lines = f.readlines()
#     for line in lines:
#         data = line.split(" ")
#         print(len(data))
