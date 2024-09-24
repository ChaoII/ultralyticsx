from collections import Counter
from pathlib import Path

import pandas as pd
import yaml

from .detection_dataset_draw_widget import DetectionDatasetDrawWidget
from ..common.dataset_detail_widget_base import DatasetDetailWidgetBase
from ..common.label_table_Widget import SplitLabelInfo
from ...types import DatasetType


class DetectionDatasetDetailWidget(DatasetDetailWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("detect_dataset")

    def set_draw_widget(self):
        draw_widget = DetectionDatasetDrawWidget()
        self.draw_widget = draw_widget
        self.hly_content.addWidget(draw_widget)

    def load_split_info(self, dataset_df: pd.DataFrame) -> list[SplitLabelInfo]:
        with open(Path(self._dataset_info.dataset_dir) / "split" / "coco_cpy.yaml", "r", encoding="utf8") as f:
            config_info = yaml.safe_load(f)
        classes = config_info.get("names", dict())
        all_num = dataset_df.shape[0]
        train_num = dataset_df.groupby("type").groups[DatasetType.TRAIN.value].size
        val_num = dataset_df.groupby("type").groups[DatasetType.VAL.value].size
        test_num = dataset_df.groupby("type").groups[DatasetType.TEST.value].size
        info = SplitLabelInfo(label="All images", all_num=all_num, train_num=train_num, val_num=val_num,
                              test_num=test_num)

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
        df_counter = df_counter.reset_index(names="label")
        df_counter["label"] = df_counter["label"].astype(int)
        df_all = pd.concat([df_sum, df_counter], axis=0)
        for row in df_all.iterrows():
            key, value = row
            label = value["label"]
            if label == -1:
                label = "All labels"
            else:
                label = classes.get(label, label)
            train_num = value[DatasetType.TRAIN.value]
            val_num = value[DatasetType.VAL.value]
            test_num = value[DatasetType.TEST.value]
            label_num = train_num + val_num + test_num
            dataset_split_num_info.append(SplitLabelInfo(label=label,
                                                         all_num=label_num,
                                                         train_num=train_num,
                                                         val_num=val_num,
                                                         test_num=test_num
                                                         ))

        return dataset_split_num_info
