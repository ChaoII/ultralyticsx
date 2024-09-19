from pathlib import Path

from common.model_type_widget import ModelType
from ..dataset_process.classify.classify_split_dataset import classify_dataset_split


def split_dataset(dataset_dir: Path, split_rates: list, model_type: ModelType):
    if model_type == ModelType.CLASSIFY:
        return classify_dataset_split(dataset_dir, split_rates)
