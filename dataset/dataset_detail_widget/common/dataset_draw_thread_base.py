from pathlib import Path

import pandas as pd
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap, QColor

from common.utils import generate_color_map


class DatasetDrawThreadBase(QThread):
    draw_one_image = Signal(str, QPixmap)

    def __init__(self):
        super().__init__()
        self.max_draw_num = 50
        self.draw_labels = False
        self.color_list: list[QColor] = []
        self.labels = []
        self.image_paths: pd.DataFrame = pd.DataFrame()

    def set_dataset_path(self, dataset_paths: list[Path]):
        self.image_paths = dataset_paths

    def set_dataset_label(self, labels):
        self.labels = list(labels)
        self.color_list = generate_color_map(len(labels))

    def set_draw_labels_status(self, status: bool):
        self.draw_labels = status

    def set_max_draw_nums(self, max_draw_num: int):
        self.max_draw_num = max_draw_num

    def run(self):
        raise NotImplementedError
