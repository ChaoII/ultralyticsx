from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase


class CustomFluentIcon(FluentIconBase, Enum):
    """ Custom icons """
    CIRCLE = "circle"
    CLASSIFY = "classify"
    DATASET = "dataset"
    DATASET1 = "dataset1"
    DETAIL = "detail"
    DETAIL1 = "detail1"
    DETECT = "detect"
    EXIT = "exit"
    FILE = "file"
    FILL_DIRECTORY = "fill_directory"
    FOLD = "fold"
    IMPORT = "import"
    IMPORT1 = "import1"
    LINE = "line"
    MODEL_EXPORT = "model_export"
    MOUSE_POINTER = "mouse_pointer"
    NEXT = "next"
    OBB = "obb"
    POINT = "point"
    POLYGON = "polygon"
    POSE = "pose"
    SEGMENT = "segment"
    SHOW = "show"
    UNFOLD = "unfold"

    def path(self, theme=Theme.AUTO):
        # getIconColor() 根据主题返回字符串 "white" 或者 "black"
        return f'./resource/icons/{self.value}_{getIconColor(theme)}.svg'
