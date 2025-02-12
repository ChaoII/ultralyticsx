from pathlib import Path

from common.component.model_type_widget import ModelType
from dataset.dataset_process.utils import classify_dataset_check, coco_dataset_check


class DatasetCheck:
    def __init__(self, model_type: ModelType):
        self.model_type = model_type

    def check(self, dataset_dir: Path | str) -> bool:
        if self.model_type == ModelType.CLASSIFY:
            return classify_dataset_check(dataset_dir)
        if self.model_type == ModelType.DETECT:
            return coco_dataset_check(dataset_dir)
        if self.model_type == ModelType.OBB:
            return coco_dataset_check(dataset_dir)
        if self.model_type == ModelType.SEGMENT:
            return coco_dataset_check(dataset_dir)
        if self.model_type == ModelType.POSE:
            return coco_dataset_check(dataset_dir)
        return False
