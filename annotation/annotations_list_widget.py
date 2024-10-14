from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QListWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import ColorPickerButton, BodyLabel, SimpleCardWidget, StrongBodyLabel, ListWidget

from common.component.custom_color_button import CustomColorButton
from common.component.custom_scroll_widget import CustomScrollWidget
from common.utils.utils import generate_random_color


class AnnotationListItemWidget(QWidget):

    def __init__(self, annotation: str):
        super().__init__()
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)

        color_btn = CustomColorButton(generate_random_color())
        color_btn.setFixedSize(16, 16)
        color_btn.set_border_radius(8)

        self.hly.addWidget(color_btn)
        self.hly.addWidget(BodyLabel(text=annotation))

    def get_label(self):
        return self.hly.itemAt(1).widget().text()


class AnnotationListWidget(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("annotationListWidget")
        self.setFixedWidth(200)
        self.setMinimumHeight(200)
        self.lbl_title = StrongBodyLabel(text=self.tr("annotations"))
        self.list_widget = ListWidget()
        self.vly_content = QVBoxLayout(self)
        self.vly_content.addWidget(self.lbl_title)
        self.vly_content.addWidget(self.list_widget)

    def connect_signals_and_slots(self):
        self.list_widget.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item: QListWidgetItem):
        self.list_widget.itemWidget(item)

    def add_annotation(self, annotation):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, AnnotationListItemWidget(annotation))
