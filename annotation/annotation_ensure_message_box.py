from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QWidget, QListWidgetItem
from qfluentwidgets import MessageBoxBase, BodyLabel, ColorPickerButton, StrongBodyLabel, LineEdit

from common.component.custom_list_widget import CustomListWidget


class LabelListItemWidget(QWidget):
    def __init__(self, label: str, color: QColor, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = ColorPickerButton(color, "")
        self.cb_label_status.setFixedSize(16, 16)
        self.hly.addWidget(self.cb_label_status)
        self.hly.addWidget(BodyLabel(text=label))
        self.label = label

    def get_label(self):
        return self.label


class AnnotationEnsureMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, labels_color: dict, parent=None):
        super().__init__(parent)
        self.title_label = StrongBodyLabel(self.tr("Select the label"), self)
        self.le_label = LineEdit()
        self.list_widget = CustomListWidget()
        # 将组件添加到布局中
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.le_label)
        self.viewLayout.addWidget(self.list_widget)
        self.set_labels(labels_color)
        self.list_widget.itemClicked.connect(self.on_label_item_clicked)

    def set_labels(self, labels_color: dict):
        self.list_widget.clear()
        for label, color in labels_color.items():
            item = QListWidgetItem()
            self.list_widget.addItem(item)
            label_item = LabelListItemWidget(label, color)
            self.list_widget.setItemWidget(item, label_item)

        labels = list(labels_color.keys())
        if len(labels) > 0:
            self.list_widget.setCurrentIndex(self.list_widget.model().index(0, 0))
            self.le_label.setText(labels[0])

    def on_label_item_clicked(self, item: QListWidgetItem):
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, LabelListItemWidget):
            self.le_label.setText(widget.get_label())

    def get_label(self):
        return self.le_label.text()
