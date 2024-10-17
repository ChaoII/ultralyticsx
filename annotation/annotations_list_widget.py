from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QKeyEvent, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QListWidgetItem, QTableWidget
from qfluentwidgets import ColorPickerButton, BodyLabel, SimpleCardWidget, StrongBodyLabel

from annotation.core import drawing_status_manager, DrawingStatus
from common.component.custom_list_widget import CustomListWidget


class AnnotationListItemWidget(QWidget):
    item_deleted = Signal(str)

    def __init__(self, uid: str, annotation: str, color: QColor, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = ColorPickerButton(color, "")
        self.cb_label_status.setFixedSize(16, 16)
        self.hly.addWidget(self.cb_label_status)
        self.hly.addWidget(BodyLabel(text=annotation))
        self.hly.addStretch(1)
        self.annotation = annotation
        self.uid = uid

    def get_annotation(self):
        return self.annotation


class AnnotationListWidget(SimpleCardWidget):
    delete_annotation_clicked = Signal(str)
    annotation_item_selected_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("annotationLIstWidget")
        self.setFixedWidth(200)
        self.setMinimumHeight(200)

        self.lbl_title = StrongBodyLabel(text=self.tr("Annotations"))
        self.lbl_title.setFixedHeight(20)

        self.list_widget = CustomListWidget()
        self.list_widget.setAutoFillBackground(True)
        self.list_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.hly_lbl = QHBoxLayout()
        self.hly_lbl.addWidget(self.lbl_title)
        self.hly_lbl.addStretch(1)

        self.vly_content = QVBoxLayout(self)
        self.vly_content.addLayout(self.hly_lbl)
        self.vly_content.addWidget(self.list_widget)
        self.annotation_item_map = dict()
        self.list_widget.itemClicked.connect(self.on_annotation_item_clicked)

    def clear(self):
        self.list_widget.clear()

    def add_annotation(self, uid: str, annotation: str, color: QColor):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        annotation_item_widget = AnnotationListItemWidget(uid, annotation, color)
        annotation_item_widget.item_deleted.connect(self.on_delete_item)
        self.list_widget.setItemWidget(item, annotation_item_widget)
        self.annotation_item_map.update({uid: item})

    def on_delete_item(self, uid: str):
        self.delete_annotation_item(uid)

    def on_annotation_item_clicked(self, item: QListWidgetItem):
        annotation_item_widget = self.list_widget.itemWidget(item)
        if isinstance(annotation_item_widget, AnnotationListItemWidget):
            self.annotation_item_selected_changed.emit(annotation_item_widget.uid)

    def delete_annotation_item(self, uid: str):
        item = self.annotation_item_map.get(uid, None)
        if item is None:
            return
        self.list_widget.removeItemWidget(item)
        self.list_widget.takeItem(self.list_widget.row(item))
        self.annotation_item_map.pop(uid)
        self.delete_annotation_clicked.emit(uid)

    def set_selected_item(self, uid: str):
        item = self.annotation_item_map.get(uid, None)
        if item is not None:
            self.list_widget.setCurrentItem(item)

    def delete_annotation_item_by_annotation(self, annotation: str):
        uids = []
        for uid, item in self.annotation_item_map.items():
            widget = self.list_widget.itemWidget(item)
            if isinstance(widget, AnnotationListItemWidget):
                if widget.get_annotation() == annotation:
                    uids.append(uid)
        for uid in uids:
            self.delete_annotation_item(uid)

    def update_annotation_item_color(self, annotation: str, color: QColor):
        for uid, item in self.annotation_item_map.items():
            widget = self.list_widget.itemWidget(item)
            if isinstance(widget, AnnotationListItemWidget):
                if widget.get_annotation() == annotation:
                    widget.cb_label_status.setColor(color)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if event.key() == Qt.Key.Key_Delete:
                uid = ""
                item = self.list_widget.currentItem()
                widget = self.list_widget.itemWidget(item)
                if isinstance(widget, AnnotationListItemWidget):
                    uid = widget.uid
                self.delete_annotation_item(uid)
