import pandas as pd

from dataset.dataset_detail_widget.classify.classify_dataset_draw_widget import ClassifyDatasetDrawWidget
from dataset.dataset_detail_widget.common.dataset_detail_widget_base import DatasetDetailWidgetBase
from dataset.dataset_detail_widget.common.label_table_Widget import SplitLabelInfo
from dataset.types import DatasetType


class ClassifyDatasetDetailWidget(DatasetDetailWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")

    def set_draw_widget(self):
        draw_widget = ClassifyDatasetDrawWidget()
        self.draw_widget = draw_widget
        self.hly_content.addWidget(draw_widget)
    def load_split_info(self, dataset_df: pd.DataFrame) -> list[SplitLabelInfo]:
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
        return dataset_split_num_info
