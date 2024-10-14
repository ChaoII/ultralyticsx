from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import Dialog

from annotation.annotation_command_bar import AnnotationCommandBar
from annotation.annotations_list_widget import AnnotationListWidget
from annotation.canvas_widget import InteractiveCanvas
from annotation.image_list_widget import ImageListWidget
from annotation.labels_settings_widget import LabelSettingsWidget
from common.core.interface_base import InterfaceBase
from common.utils.utils import is_image


class AnnotationInterface(InterfaceBase):
    def update_widget(self):
        pass

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("annotation_interface")
        self.vly = QVBoxLayout(self)
        self.vly.setContentsMargins(10, 10, 10, 10)
        self.vly.setSpacing(9)

        self.cb_label = AnnotationCommandBar(self)
        self.canvas = InteractiveCanvas()
        self.label_widget = LabelSettingsWidget()
        self.annotation_widget = AnnotationListWidget()
        self.image_list_widget = ImageListWidget()

        self.vly_right = QVBoxLayout()
        self.vly_right.setContentsMargins(0, 0, 0, 0)
        self.vly_right.addWidget(self.label_widget)
        self.vly_right.addWidget(self.annotation_widget)
        self.vly_right.addWidget(self.image_list_widget)
        # self.vly_right.addStretch(1)
        self.hly = QHBoxLayout()
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.hly.setSpacing(4)
        self.hly.addWidget(self.canvas)
        self.hly.addLayout(self.vly_right)
        self.vly.addWidget(self.cb_label)
        self.vly.addLayout(self.hly)
        self.connect_signals_and_slots()

        self.current_dataset_path: Path | None = None
        self.labels = []

    def connect_signals_and_slots(self):
        self.cb_label.save_annotation_clicked.connect(self.save_current_annotation)
        self.cb_label.delete_image_clicked.connect(self.on_delete_image_clicked)
        self.cb_label.pre_image_clicked.connect(self.on_pre_image_clicked)
        self.cb_label.next_image_clicked.connect(self.on_next_image_clicked)
        self.cb_label.shape_selected.connect(lambda x: self.canvas.set_shape_type(x))
        self.cb_label.scale_down_clicked.connect(lambda: self.canvas.scale_down())
        self.cb_label.scale_up_clicked.connect(lambda: self.canvas.scale_up())
        self.cb_label.current_path_changed.connect(self.on_current_path_changed)
        self.label_widget.add_label_clicked.connect(self.on_add_label)
        self.label_widget.delete_label_clicked.connect(self.on_delete_label)
        self.image_list_widget.image_item_changed.connect(self.on_image_item_changed)
        self.image_list_widget.item_ending_status_changed.connect(self.on_move_ending_status)

    def on_add_label(self, label: str):
        self.labels.append(label)
        self.label_widget.set_labels(self.labels)

    def on_delete_label(self, label: str):
        self.labels.remove(label)
        self.label_widget.set_labels(self.labels)

    def on_move_ending_status(self, status: int):
        if status == 0:
            self.cb_label.action_pre_image.setEnabled(False)
            self.cb_label.action_next_image.setEnabled(True)
        elif status == 1:
            self.cb_label.action_next_image.setEnabled(False)
            self.cb_label.action_pre_image.setEnabled(True)
        elif status == 2:
            self.cb_label.action_pre_image.setEnabled(True)
            self.cb_label.action_next_image.setEnabled(True)

    def on_image_item_changed(self, image_path: str):
        self.canvas.set_image(image_path)

    def on_save_current_annotation(self):
        self.save_current_annotation()

    def on_delete_image_clicked(self):
        pass

    def on_pre_image_clicked(self):
        _, labeled = self.image_list_widget.get_current_image_labeled()
        if not labeled:
            w = Dialog(self.tr("Warning"),
                       self.tr("Current annotation is not saved. Do you want to save it?"), self)
            w.yesButton.setText(self.tr("Save"))
            if w.exec():
                self.save_current_annotation()
                self.image_list_widget.set_current_image_labeled()
            else:
                return
        self.image_list_widget.pre_item()

    def on_next_image_clicked(self):
        _, labeled = self.image_list_widget.get_current_image_labeled()
        if not labeled:
            w = Dialog(self.tr("Warning"),
                       self.tr("Current annotation is not saved. Do you want to save it?"), self)
            w.yesButton.setText(self.tr("Save"))
            if w.exec():
                self.save_current_annotation()
                self.image_list_widget.set_current_image_labeled()
            else:
                return
        self.image_list_widget.next_item()

    def on_current_path_changed(self, path: Path):
        if path.exists():
            if path.is_file() and is_image(path):
                self.canvas.set_image(path)
                self.current_dataset_path = path.parent
            elif path.is_dir():
                self.label_widget.clear()
                self.canvas.clear()
                self.image_list_widget.clear()
                self.image_list_widget.set_image_dir_path(path)
                self.current_dataset_path = path
                label_file_path = path / "classes.txt"
                if label_file_path.exists():
                    self.labels = open(label_file_path).read().splitlines()
                    self.label_widget.set_labels(self.labels)

    def save_current_annotation(self):
        if self.current_dataset_path:
            if self.current_dataset_path.exists():
                annotation_dir = self.current_dataset_path / "annotations"
                if not annotation_dir.exists():
                    w = Dialog(self.tr("Warning"),
                               self.tr("annotation directory is ot existed,Create it?"), self)
                    w.yesButton.setText(self.tr("Yes"))
                    w.cancelButton.setText(self.tr("No"))
                    if w.exec():
                        annotation_dir.mkdir(exist_ok=True)
                    else:
                        return
            label_file_path = self.current_dataset_path / "classes.txt"
            with open(label_file_path, "w", encoding="utf8") as f:
                f.writelines([""])

            annotation_name = Path(self.image_list_widget.get_current_image_labeled()[0])
            annotation_path = self.current_dataset_path / "annotations" / (annotation_name.name + ".txt")
            with open(annotation_path, "w", encoding="utf8") as f:
                f.writelines(["1", "2", "3", "4"])

            self.image_list_widget.set_current_image_labeled()
