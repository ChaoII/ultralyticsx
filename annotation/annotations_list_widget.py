from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QKeyEvent, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QListWidgetItem, QTableWidget
from qfluentwidgets import BodyLabel, SimpleCardWidget, StrongBodyLabel

from annotation.core import drawing_status_manager, DrawingStatus
from common.component.custom_color_button import CustomColorButton
from common.component.custom_list_widget import CustomListWidget


class AnnotationListItemWidget(QWidget):
    item_deleted = Signal(str)
    item_edited = Signal(str)

    def __init__(self, item_id: str, annotation: str, color: QColor, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = CustomColorButton(color)
        self.cb_label_status.setFixedSize(16, 16)
        self.lbl_annotation = BodyLabel(annotation, self)
        self.hly.addWidget(self.cb_label_status)
        self.hly.addWidget(self.lbl_annotation)
        self.hly.addStretch(1)
        self.annotation = annotation
        self.item_id = item_id
        self.cb_label_status.clicked.connect(lambda: self.item_edited.emit(self.item_id))

    def set_color(self, color: QColor):
        self.cb_label_status.setColor(color)

    def set_text(self, annotation: str):
        self.lbl_annotation.setText(annotation)

    def get_annotation(self):
        return self.annotation


class AnnotationListWidget(SimpleCardWidget):
    delete_annotation_clicked = Signal(str)
    edit_annotation_clicked = Signal(str)
    annotation_item_selected_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("annotationLIstWidget")
        self.setMinimumHeight(200)
        self.lbl_title = StrongBodyLabel(text=self.tr("Annotations"))
        self.lbl_title.setFixedHeight(20)

        self.list_widget = CustomListWidget()
        self.list_widget.setAutoFillBackground(True)
        self.list_widget.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.list_widget.set_item_height(25)

        self.hly_lbl = QHBoxLayout()
        self.hly_lbl.addWidget(self.lbl_title)
        self.hly_lbl.addStretch(1)

        self.vly_content = QVBoxLayout(self)
        self.vly_content.addLayout(self.hly_lbl)
        self.vly_content.addWidget(self.list_widget)
        self.annotation_item_map = dict()
        self.list_widget.itemClicked.connect(self.on_annotation_item_clicked)
        self.list_widget.itemSelectionChanged.connect(self.on_annotation_item_selected_changed)

    def on_annotation_item_selected_changed(self):
        item_ids = []
        for item in self.list_widget.selectedItems():
            if item.isSelected():
                annotation_item_widget = self.list_widget.itemWidget(item)
                if isinstance(annotation_item_widget, AnnotationListItemWidget):
                    item_ids.append(annotation_item_widget.item_id)
        self.annotation_item_selected_changed.emit(item_ids)

    def clear(self):
        self.list_widget.clear()

    def add_annotation(self, item_id: str, annotation: str, color: QColor):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        annotation_item_widget = AnnotationListItemWidget(item_id, annotation, color)
        annotation_item_widget.item_deleted.connect(self.on_delete_item)
        annotation_item_widget.item_edited.connect(self.on_edit_item)
        self.list_widget.setItemWidget(item, annotation_item_widget)
        self.annotation_item_map.update({item_id: item})

    def on_delete_item(self, item_id: str):
        self.delete_annotation_item(item_id)

    def on_edit_item(self, item_id: str):
        self.edit_annotation_clicked.emit(item_id)

    def set_item_color(self, item_id: str, color: QColor):
        item = self.annotation_item_map.get(item_id, None)
        if item is None:
            return
        annotation_item_widget = self.list_widget.itemWidget(item)
        if isinstance(annotation_item_widget, AnnotationListItemWidget):
            annotation_item_widget.set_color(color)

    def set_item_annotation(self, item_id: str, annotation: str):
        item = self.annotation_item_map.get(item_id, None)
        if item is None:
            return
        annotation_item_widget = self.list_widget.itemWidget(item)
        if isinstance(annotation_item_widget, AnnotationListItemWidget):
            annotation_item_widget.set_text(annotation)

    def on_annotation_item_clicked(self, item: QListWidgetItem):
        annotation_item_widget = self.list_widget.itemWidget(item)
        if isinstance(annotation_item_widget, AnnotationListItemWidget):
            # self.annotation_item_selected_changed.emit(annotation_item_widget.item_id)
            pass

    def delete_annotation_item(self, item_id: str):
        item = self.annotation_item_map.get(item_id, None)
        if item is None:
            return
        self.list_widget.removeItemWidget(item)
        self.list_widget.takeItem(self.list_widget.row(item))
        self.annotation_item_map.pop(item_id)
        self.delete_annotation_clicked.emit(item_id)

    def set_selected_item(self, item_ids: list[str]):
        self.list_widget.blockSignals(True)
        self.list_widget.clearSelection()
        for item_id, item in self.annotation_item_map.items():
            if item_id in item_ids:
                item.setSelected(True)
        self.list_widget.blockSignals(False)

    def delete_annotation_item_by_annotation(self, annotation: str):
        for item_id, item in self.annotation_item_map.items():
            widget = self.list_widget.itemWidget(item)
            if isinstance(widget, AnnotationListItemWidget):
                if widget.get_annotation() == annotation:
                    self.delete_annotation_item(item_id)

    def update_annotation_item_color(self, annotation: str, color: QColor):
        for _, item in self.annotation_item_map.items():
            widget = self.list_widget.itemWidget(item)
            if isinstance(widget, AnnotationListItemWidget):
                if widget.get_annotation() == annotation:
                    widget.cb_label_status.setColor(color)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if event.key() == Qt.Key.Key_Delete:
                item = self.list_widget.currentItem()
                widget = self.list_widget.itemWidget(item)
                if isinstance(widget, AnnotationListItemWidget):
                    self.delete_annotation_item(widget.item_id)
