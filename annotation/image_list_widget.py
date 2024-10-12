from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QListWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import ColorPickerButton, BodyLabel, SimpleCardWidget, StrongBodyLabel, ListWidget, CheckBox

from common.component.custom_color_button import CustomColorButton
from common.component.custom_scroll_widget import CustomScrollWidget
from common.utils.utils import generate_random_color


class ImageListItemWidget(QWidget):

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = CheckBox()
        self.hly.addWidget(self.cb_label_status)
        self.hly.addWidget(BodyLabel(text=image_path))
        self.setToolTip(image_path)

    def set_label_status(self, labeled=False):
        self.cb_label_status.setChecked(labeled)


class ImageListWidget(SimpleCardWidget):
    def __init__(self, image_dir_path=Path("."), parent=None):
        super().__init__(parent=parent)
        self.setObjectName("imageListWidget")
        self.setFixedWidth(200)
        self.setMinimumHeight(200)
        self.lbl_title = StrongBodyLabel(text=self.tr("Image list"))
        self.list_widget = ListWidget()
        self.vly_content = QVBoxLayout(self)
        self.vly_content.addWidget(self.lbl_title)
        self.vly_content.addWidget(self.list_widget)
        self.set_image_dir_path(image_dir_path)

    def set_image_dir_path(self, image_dir_path: Path):
        if image_dir_path.exists():
            has_label_list = []
            annotation_path = image_dir_path / "annotations"
            if annotation_path.exists():
                for annotation in annotation_path.iterdir():
                    has_label_list.append(annotation.resolve().as_posix())

            for image_path in image_dir_path.iterdir():
                if image_path.suffix in [".jpg", ".png", ".jpeg"]:
                    self.add_image_item(image_path.absolute(), image_path.resolve().as_posix() in has_label_list)

    def add_image_item(self, image_path, labeled=False):
        item = QListWidgetItem()
        image_list_item_widget = ImageListItemWidget(image_path.resolve().as_posix())
        image_list_item_widget.set_label_status(labeled)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, image_list_item_widget)
