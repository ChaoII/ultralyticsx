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
    FILL_DIRECTORY = "fill_directory"
    FOLD = "fold"
    IMPORT = "import"
    IMPORT1 = "import1"
    OBB = "obb"
    POSE = "pose"
    SEGMENT = "segment"
    UNFOLD = "unfold"

    def path(self, theme=Theme.AUTO):
        # getIconColor() 根据主题返回字符串 "white" 或者 "black"
        return f'./resource/icons/{self.value}_{getIconColor(theme)}.svg'
