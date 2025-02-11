import pandas as pd

from .classify_dataset_draw_thread import ClassifyDatasetDrawThread
from ..common.dataset_draw_widget_base import DatasetDrawWidgetBase
from ...types import DatasetType


class ClassifyDatasetDrawWidget(DatasetDrawWidgetBase):

    def __init__(self):
        super().__init__()

    def set_dataset_draw_thread(self):
        self.dataset_draw_thread = ClassifyDatasetDrawThread()

    def init_dataset_labels(self, dataset_df: pd.DataFrame):
        self.dataset_draw_thread.set_dataset_label(dataset_df.groupby("label").groups.keys())
        self.cmb_dataset_label.clear()
        self.cmb_dataset_label.addItems(["all"] + list(dataset_df.groupby("label").groups.keys()))

    def get_current_condition_dataset(self) -> pd.DataFrame:
        if self.dataset_type == DatasetType.ALL:
            if self.dataset_label == "all":
                image_paths = self._dataset_df.loc[:, ["image_path", "label"]]
            else:
                image_paths = self._dataset_df[self._dataset_df["label"] ==
                                               self.dataset_label].loc[:, ["image_path", "label"]]
        else:
            data_dict = self._dataset_df[self._dataset_df["type"] == self.dataset_type.value]
            if self.dataset_label == "all":
                image_paths = data_dict.loc[:, ["image_path", "label"]]
            else:
                image_paths = data_dict[data_dict["label"] == self.dataset_label].loc[:, ["image_path", "label"]]
        return image_paths
