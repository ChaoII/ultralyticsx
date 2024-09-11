import pandas as pd
import pickle

df_path = r"C:\Users\84945\Desktop\ultralytics_workspace\dataset\D000000\split_cache1"

dataset_frame: pd.DataFrame = pickle.load(open(df_path, "rb"))
dataset_frame.loc[dataset_frame["label"] == "bocai", "label"] = 0
dataset_frame.loc[dataset_frame["label"] == "changqiezi", "label"] = 1
dataset_frame.loc[dataset_frame["label"] == "hongxiancai", "label"] = 2
dataset_frame.loc[dataset_frame["label"] == "huluobo", "label"] = 3
dataset_frame.loc[dataset_frame["label"] == "xihongshi", "label"] = 4
dataset_frame.loc[dataset_frame["label"] == "xilanhua", "label"] = 5
df_mode: pd.DataFrame = dataset_frame[dataset_frame["type"] == "train"]
simples = df_mode.loc[:, ["image_path", "label"]].to_records(index=False)

pickle.dump(dataset_frame, open(df_path, "wb"))

print(simples)
