from pathlib import Path

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import QVBoxLayout, QListWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import BodyLabel, SimpleCardWidget, StrongBodyLabel, Dialog

from common.component.custom_color_button import CustomColorButton
from common.component.custom_list_widget import CustomListWidget
from common.utils.utils import generate_random_color


class ImageListItemWidget(QWidget):

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = CustomColorButton(generate_random_color())
        self.cb_label_status.setFixedSize(16, 16)
        self.cb_label_status.set_border_radius(8)
        self.hly.addWidget(self.cb_label_status)
        self.hly.addWidget(BodyLabel(text=image_path))

        self.setToolTip(image_path)
        self.image_path = image_path
        self.labeled = False

    def get_image_path(self) -> str:
        return self.image_path

    def set_label_status(self, labeled=False):
        self.labeled = labeled
        self.cb_label_status.setColor(Qt.GlobalColor.green if labeled else Qt.GlobalColor.red)

    def get_image_labeled_info(self) -> tuple[str, bool]:
        return self.image_path, self.labeled


class ImageListWidget(SimpleCardWidget):
    image_item_changed = Signal(str)
    item_ending_status_changed = Signal(int)
    save_annotation_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("imageListWidget")
        self.setFixedWidth(200)
        self.setMinimumHeight(200)
        self.lbl_title = StrongBodyLabel(text=self.tr("Image list"))
        self.list_widget = CustomListWidget()
        self.list_widget.set_item_height(25)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.addWidget(self.lbl_title)
        self.vly_content.addWidget(self.list_widget)
        self.connect_signals_and_slots()
        self.last_item = QListWidgetItem()
        self.item_widgets = []

    def connect_signals_and_slots(self):
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item: QListWidgetItem):
        row = self.list_widget.indexFromItem(item).row()
        if row == 0:
            self.item_ending_status_changed.emit(0)
        elif row == self.list_widget.count() - 1:
            self.item_ending_status_changed.emit(1)
        else:
            self.item_ending_status_changed.emit(2)
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            self.image_item_changed.emit(widget.get_image_path())

    def set_image_dir_path(self, image_path_list: list[Path], annotation_list: list):
        if len(image_path_list) == 0:
            self.item_ending_status_changed.emit(3)
            return
        elif len(image_path_list) == 1:
            self.item_ending_status_changed.emit(3)
        else:
            self.item_ending_status_changed.emit(0)
        for image_path in image_path_list:
            self.add_image_item(image_path, image_path.stem in annotation_list)
        self.list_widget.setCurrentIndex(self.list_widget.model().index(0, 0))
        self.last_item = self.list_widget.item(0)
        widget = self.list_widget.itemWidget(self.last_item)
        if isinstance(widget, ImageListItemWidget):
            self.image_item_changed.emit(widget.get_image_path())

    def clear(self):
        self.list_widget.clear()
        self.update_item_widgets()

    def add_image_item(self, image_path, labeled=False):
        item = QListWidgetItem()
        image_list_item_widget = ImageListItemWidget(image_path.resolve().as_posix())
        image_list_item_widget.set_label_status(labeled)
        image_list_item_widget.installEventFilter(self)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, image_list_item_widget)
        self.update_item_widgets()

    def delete_current_image_item(self):
        item = self.list_widget.currentItem()
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            self.list_widget.removeItemWidget(item)
            self.list_widget.takeItem(self.list_widget.row(item))
        item = self.list_widget.currentItem()
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            self.image_item_changed.emit(widget.get_image_path())
        self.update_item_widgets()

    def update_item_widgets(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            self.item_widgets.append(widget)

    def next_item(self):
        current_index = self.list_widget.currentIndex()
        current_row = current_index.row()
        self.last_item = self.list_widget.item(current_row)
        if current_row == self.list_widget.count() - 1:
            return
        next_row = current_row + 1
        next_index = self.list_widget.model().index(next_row, 0)
        self.list_widget.setCurrentIndex(next_index)
        item = self.list_widget.item(next_row)
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            self.image_item_changed.emit(widget.get_image_path())

        if next_row == self.list_widget.count() - 1:
            self.item_ending_status_changed.emit(1)
        else:
            self.item_ending_status_changed.emit(2)

    def pre_item(self):
        current_index = self.list_widget.currentIndex()
        current_row = current_index.row()
        self.last_item = self.list_widget.item(current_row)
        if current_row == 0:
            return
        pre_row = current_row - 1
        pre_index = self.list_widget.model().index(pre_row, 0)
        self.list_widget.setCurrentIndex(pre_index)
        item = self.list_widget.item(pre_row)
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            self.image_item_changed.emit(widget.get_image_path())
        if pre_row == 0:
            self.item_ending_status_changed.emit(0)
        else:
            self.item_ending_status_changed.emit(2)

    def set_current_image_labeled(self, labeled: bool):
        item = self.list_widget.currentItem()
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            widget.set_label_status(labeled)

    def get_current_image_labeled(self) -> [str, bool]:
        item = self.list_widget.currentItem()
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, ImageListItemWidget):
            return widget.get_image_labeled_info()
        return "", False

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Type.MouseButtonPress:
            if obj in self.item_widgets:
                item = self.list_widget.currentItem()
                widget = self.list_widget.itemWidget(item)
                if isinstance(widget, ImageListItemWidget):
                    label = widget.get_image_labeled_info()[1]
                    # 如果未标注直接拦截
                    if not label:
                        w = Dialog(self.tr("Warning"),
                                   self.tr("Current annotation is not saved. Do you want to save it?"), self)
                        if w.exec():
                            self.save_annotation_clicked.emit()
        return super().eventFilter(obj, e)
