import pickle
from pathlib import Path
import types
import pandas as pd
import ultralytics.data.utils as utils


def check_cls_dataset_patch(dataset, split=""):
    print("=====================================================================")
    dataset = Path(dataset)
    df: pd.DataFrame = pickle.load(open(dataset / "split_cache1", "rb"))
    nc = len(df.groupby("label").groups)
    names = dict(enumerate(sorted(list(df.groupby("label").groups.keys()))))
    data = {"train": dataset, "val": dataset, "test": dataset, "nc": nc, "names": names}
    return data


utils.check_cls_dataset = check_cls_dataset_patch
