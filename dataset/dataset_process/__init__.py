import pickle
from pathlib import Path

from .dataset_checker import check_dataset
from .dataset_spliter import split_dataset


def load_split_dataset(dataset_dir: Path):
    dataset_df = pickle.load(open(dataset_dir / "split_cache", "rb"))
    return dataset_df
