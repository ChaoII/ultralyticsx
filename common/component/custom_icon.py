from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase


class CustomFluentIcon(FluentIconBase, Enum):
    """ Custom icons """

    CLASSIFY = "classify"
    DATASET = "dataset"
    DATASET1 = "dataset1"
    DETAIL = "detail"
    DETAIL1 = "detail1"
    DETECT = "detect"
    EXIT = "exit"
    FILL_DIRECTORY = "fill_directory"
    FOLD = "fold"
    IMPORT = "import"
    IMPORT1 = "import1"
    MODEL_EXPORT = "model_export"
    NEXT = "next"
    OBB = "obb"
    POSE = "pose"
    SEGMENT = "segment"
    SHOW = "show"
    UNFOLD = "unfold"

    def path(self, theme=Theme.AUTO):
        # getIconColor() 根据主题返回字符串 "white" 或者 "black"
        return f'./resource/icons/{self.value}_{getIconColor(theme)}.svg'
