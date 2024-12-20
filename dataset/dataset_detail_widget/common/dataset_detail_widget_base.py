from collections import Counter
from pathlib import Path

import pandas as pd
import yaml
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from common.database.db_helper import db_session
from models.models import Dataset
from .dataset_draw_widget_base import DatasetDrawWidgetBase
from .label_table_Widget import SplitLabelInfo, DatasetLabelsInfoWidget
from ...dataset_process import split_dataset, load_split_dataset
from ...types import DatasetInfo, DatasetStatus, DatasetType


class DatasetDetailWidgetBase(QWidget):
    load_dataset_finished = Signal(int, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")
        self.labels_widget = DatasetLabelsInfoWidget()
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.setContentsMargins(0, 0, 0, 0)
        self.draw_widget: DatasetDrawWidgetBase | None = None

        self.hly_content = QHBoxLayout()
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.hly_content.setSpacing(0)
        self.hly_content.addWidget(self.labels_widget)

        self._dataset_info: DatasetInfo = DatasetInfo()
        self.vly_dataset_info.addLayout(self.hly_content)
        self._dataset_map = dict()
        self._total_dataset = 0
        self._split_rates = []
        self.set_draw_widget()

    def set_draw_widget(self):
        raise NotImplementedError

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self._dataset_info = dataset_info
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=dataset_info.dataset_id).first()
            self._split_rates = [int(rate) for rate in dataset.split_rate.split("_")]
            self._total_dataset = dataset.dataset_total
        if dataset_info.dataset_status == DatasetStatus.CHECKED:
            dataset_df = load_split_dataset(Path(self._dataset_info.dataset_dir))
            self._load_dataset(dataset_df)
        else:
            self.split_dataset(self._split_rates)

    def get_dataset_split(self):
        return self._total_dataset, self._split_rates

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
        df_counter = pd.DataFrame(labels_map).fillna(0).astype(int).sort_index()
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

    def _load_dataset(self, dataset_df: pd.DataFrame):
        split_info = self.load_split_info(dataset_df)
        self.labels_widget.update_table(self._split_rates, split_info)
        self.draw_widget.update_dataset(dataset_df)
        self.load_dataset_finished.emit(self._total_dataset, self._split_rates)

    @Slot(list)
    def split_dataset(self, split_rates):
        self._split_rates = split_rates
        dataset_df = split_dataset(Path(self._dataset_info.dataset_dir), self._split_rates,
                                   self._dataset_info.model_type)
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=self._dataset_info.dataset_id).first()
            dataset.dataset_total = dataset_df.shape[0]
        self._load_dataset(dataset_df)
