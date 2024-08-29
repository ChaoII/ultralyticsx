import enum
from enum import Enum

from PySide6.QtGui import QColor
from qfluentwidgets import isDarkTheme

from common.model_type_widget import ModelType


class DatasetStatus(Enum):
    WAIT_IMPORT = 0
    CHECKED = 1
    CHECK_FAILED = 2

    @property
    def color(self):
        _color_map = {
            DatasetStatus.WAIT_IMPORT: QColor("#ff6600"),
            DatasetStatus.CHECKED: QColor("#0d5f07"),
            DatasetStatus.CHECK_FAILED: QColor("#ff3333"),
        }
        if isDarkTheme():
            _color_map = {
                DatasetStatus.WAIT_IMPORT: QColor("#ffa366"),
                DatasetStatus.CHECKED: QColor("#66ff66"),
                DatasetStatus.CHECK_FAILED: QColor("#ff9999"),
            }
        return _color_map[self]


class DatasetType(enum.Enum):
    ALL = "all"
    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class DatasetInfo:
    dataset_name: str
    dataset_id: str
    dataset_description: str
    dataset_status: DatasetStatus
    dataset_dir: str
    model_type: ModelType = ModelType.CLASSIFY
    create_time: str
    split_rate: list
