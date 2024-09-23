from pathlib import Path

import pandas as pd
import yaml

from ..common.dataset_draw_widget_base import DatasetDrawWidgetBase
from .pose_dataset_draw_thread import PoseDatasetDrawThread
from ...types import DatasetType


class PoseDatasetDrawWidget(DatasetDrawWidgetBase):

    def __init__(self):
        super().__init__()

    def set_dataset_draw_thread(self):
        self.dataset_draw_thread = PoseDatasetDrawThread()

    def init_dataset_labels(self, dataset_df: pd.DataFrame):
        config_path = Path(dataset_df.loc[0, "image_path"]).parent.parent.parent / "coco_cpy.yaml"
        with open(config_path, "r", encoding="utf8") as f:
            config_info = yaml.safe_load(f)
        classes = config_info.get("names", dict())
        self.dataset_draw_thread.set_dataset_label(list(classes.values()))
        self.cmb_dataset_label.setVisible(False)

    def get_current_condition_dataset(self) -> pd.DataFrame:
        if self.dataset_type == DatasetType.ALL:
            image_paths = self._dataset_df.loc[:, ["image_path", "label_path"]]
        else:
            data_dict = self._dataset_df[self._dataset_df["type"] == self.dataset_type.value]
            image_paths = data_dict.loc[:, ["image_path", "label_path"]]
        return image_paths
