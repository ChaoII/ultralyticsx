from pathlib import Path

import pandas as pd
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from common.database.db_helper import db_session
from dataset.dataset_checker.classify.split_dataset import split_dataset, load_split_dataset
from dataset.dataset_detail_widget.classify.classify_dataset_draw_widget import ClassifyDatasetDrawWidget
from dataset.dataset_detail_widget.common.label_table_Widget import SplitLabelInfo, DatasetLabelsInfoWidget
from dataset.types import DatasetInfo, DatasetType, DatasetStatus
from models.models import Dataset


class ClassifyDataset(QWidget):
    load_dataset_finished = Signal(int, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")
        self.labels_widget = DatasetLabelsInfoWidget()
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.setContentsMargins(0, 0, 0, 0)
        self.draw_widget = ClassifyDatasetDrawWidget()

        self.hly_content = QHBoxLayout()
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.hly_content.setSpacing(0)
        self.hly_content.addWidget(self.labels_widget)
        self.hly_content.addWidget(self.draw_widget)

        self._dataset_info: DatasetInfo = DatasetInfo()
        self.vly_dataset_info.addLayout(self.hly_content)
        self._dataset_map = dict()
        self._total_dataset = 0
        self._split_rates = []

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

    def _load_dataset(self, dataset_df: pd.DataFrame):
        all_num = dataset_df.shape[0]
        train_num = dataset_df.groupby("type").groups[DatasetType.TRAIN.value].size
        val_num = dataset_df.groupby("type").groups[DatasetType.VAL.value].size
        test_num = dataset_df.groupby("type").groups[DatasetType.TEST.value].size
        info = SplitLabelInfo(label="All", all_num=all_num, train_num=train_num, val_num=val_num, test_num=test_num)
        dataset_split_num_info = [info]
        for key, group in dataset_df.groupby("label").groups.items():
            label_df = dataset_df[(dataset_df["label"] == key)]
            label_dataset_num = group.size
            train_num = label_df[label_df["type"] == DatasetType.TRAIN.value].shape[0]
            val_num = label_df[label_df["type"] == DatasetType.VAL.value].shape[0]
            test_num = label_df[label_df["type"] == DatasetType.TEST.value].shape[0]
            dataset_split_num_info.append(SplitLabelInfo(label=key,
                                                         all_num=label_dataset_num,
                                                         train_num=train_num,
                                                         val_num=val_num,
                                                         test_num=test_num))
        self.labels_widget.update_table(self._split_rates, dataset_split_num_info)
        self.draw_widget.update_dataset(dataset_df)
        self.load_dataset_finished.emit(self._total_dataset, self._split_rates)

    @Slot(list)
    def split_dataset(self, split_rates):
        self._split_rates = split_rates
        dataset_df = split_dataset(Path(self._dataset_info.dataset_dir), self._split_rates)
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=self._dataset_info.dataset_id).first()
            dataset.dataset_total = dataset_df.shape[0]
        self._load_dataset(dataset_df)
