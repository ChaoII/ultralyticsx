from pathlib import Path

import pandas as pd

from common.component.model_type_widget import ModelType
from dataset.dataset_process.utils import classify_dataset_split, coco_dataset_split


class DatasetSplit:
    def __init__(self, model_type: ModelType):
        self.model_type = model_type

    def split(self, dataset_dir: Path | str, split_rates: list | tuple) -> pd.DataFrame | None:
        if self.model_type == ModelType.CLASSIFY:
            return classify_dataset_split(dataset_dir, split_rates)
        if self.model_type == ModelType.DETECT:
            return coco_dataset_split(dataset_dir, split_rates)
        if self.model_type == ModelType.OBB:
            return coco_dataset_split(dataset_dir, split_rates)
        if self.model_type == ModelType.SEGMENT:
            return coco_dataset_split(dataset_dir, split_rates)
        if self.model_type == ModelType.POSE:
            return coco_dataset_split(dataset_dir, split_rates, True)