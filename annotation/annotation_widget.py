from pathlib import Path

from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import Dialog, InfoBar, InfoBarPosition

from annotation.annotation_command_bar import AnnotationCommandBar
from annotation.annotation_ensure_message_box import AnnotationEnsureMessageBox
from annotation.annotations_list_widget import AnnotationListWidget
from annotation.canvas_widget import InteractiveCanvas, DrawingStatus
from annotation.image_list_widget import ImageListWidget
from annotation.labels_settings_widget import LabelSettingsWidget
from annotation.shape import ShapeType, ShapeItem
from common.component.model_type_widget import ModelType
from common.core.content_widget_base import ContentWidgetBase
from common.core.window_manager import window_manager
from common.database.annotation_task_helper import db_update_annotation_dir_path
from common.database.db_helper import db_session
from common.utils.utils import is_image, generate_random_color
from models.models import AnnotationTask


class AnnotationWidget(ContentWidgetBase):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("annotation_widget")
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
        self.image_dir_path: Path | None = None
        self.annotation_dir_path: Path | None = None
        self.labels_color = dict()
        self.annotation_task_id = ""
        self.model_type = ModelType.DETECT
        self.last_selected_label = ""

    def connect_signals_and_slots(self):
        self.cb_label.annotation_directory_changed.connect(self.on_annotation_directory_changed)
        self.cb_label.save_annotation_clicked.connect(self.save_current_annotation)
        self.cb_label.delete_image_clicked.connect(self.on_delete_image_clicked)
        self.cb_label.pre_image_clicked.connect(self.on_pre_image_clicked)
        self.cb_label.next_image_clicked.connect(self.on_next_image_clicked)
        self.cb_label.shape_selected.connect(self.on_shape_clicked)
        self.cb_label.drawing_status_selected.connect(lambda x: self.canvas.set_drawing_status(x))
        self.cb_label.scale_down_clicked.connect(lambda: self.canvas.scale_down())
        self.cb_label.scale_up_clicked.connect(lambda: self.canvas.scale_up())

        self.canvas.is_drawing_changed.connect(self.on_is_drawing_changed)
        self.canvas.draw_finished.connect(self.on_draw_finished)
        self.canvas.shape_item_selected_changed.connect(self.on_shape_item_selected_changed)
        self.canvas.delete_shape_item_clicked.connect(lambda x: self.annotation_widget.delete_annotation_item(x))
        self.label_widget.add_label_clicked.connect(self.on_add_label)
        self.label_widget.delete_label_clicked.connect(self.on_delete_label)
        self.label_widget.label_item_color_changed.connect(self.on_label_item_color_changed)
        self.annotation_widget.delete_annotation_clicked.connect(lambda x: self.canvas.delete_shape_item(x))
        self.annotation_widget.edit_annotation_clicked.connect(self.on_annotation_item_edit_clicked)
        self.annotation_widget.annotation_item_selected_changed.connect(self.on_annotation_item_selected_changed)
        self.image_list_widget.image_item_changed.connect(self.on_image_item_changed)
        self.image_list_widget.item_ending_status_changed.connect(self.on_move_ending_status)
        self.image_list_widget.save_annotation_clicked.connect(lambda: self.save_current_annotation())

    def update_widget(self):
        with db_session() as session:
            annotation_task: AnnotationTask = session.query(AnnotationTask).filter(
                AnnotationTask.task_id == self.annotation_task_id).first()
            self.model_type = ModelType(annotation_task.model_type)
            if annotation_task.image_dir:
                image_path = Path(annotation_task.image_dir)
            if annotation_task.annotation_dir:
                self.annotation_dir_path = Path(annotation_task.annotation_dir)
        self.update_shape_status()
        self.set_image_path(image_path)

    def update_shape_status(self):
        if ModelType(self.model_type) == ModelType.CLASSIFY:
            self.cb_label.set_shape_enabled(False)
        elif ModelType(self.model_type) == ModelType.SEGMENT:
            self.cb_label.set_shape_enabled(False)
            self.cb_label.action_polygon.setEnabled(True)
        elif ModelType(self.model_type) == ModelType.POSE:
            self.cb_label.set_shape_enabled(False)
            self.cb_label.action_point.setEnabled(True)
        elif ModelType(self.model_type) == ModelType.DETECT:
            self.cb_label.set_shape_enabled(False)
            self.cb_label.action_rectangle.setEnabled(True)
        elif ModelType(self.model_type) == ModelType.OBB:
            self.cb_label.set_shape_enabled(False)
            self.cb_label.action_rotated_rectangle.setEnabled(True)
        else:
            self.cb_label.set_shape_enabled(False)
            self.cb_label.action_line.setEnabled(True)

    def on_add_label(self, label: str):
        if label in self.labels_color:
            w = Dialog(self.tr("Warning"),
                       self.tr("There is a same label in labels?"), self)
            w.cancelButton.hide()
            w.exec()
            return
        self.labels_color.update({label: generate_random_color()})
        self.label_widget.set_labels(self.labels_color)
        self.update_label_file()

    def on_delete_label(self, label: str):
        self.labels_color.pop(label)
        self.label_widget.set_labels(self.labels_color)
        self.annotation_widget.delete_annotation_item_by_annotation(label)
        self.update_label_file()

    def on_label_item_color_changed(self, label: str, color: QColor):
        self.labels_color[label] = color
        self.annotation_widget.update_annotation_item_color(label, color)
        self.canvas.update_shape_item_color(label, color)

    def on_is_drawing_changed(self, is_drawing: bool):
        if is_drawing:
            self.cb_label.set_shape_enabled(False)
        else:
            self.update_shape_status()

    def is_saved_annotation(self) -> bool:
        shape_num = len(self.canvas.get_shape_items()) - 1
        image_path = Path(self.image_list_widget.get_current_image_labeled()[0])
        annotation_path = self.annotation_dir_path / (image_path.stem + ".txt")
        if not annotation_path.exists():
            return False
        f = annotation_path.open("r", encoding="utf-8")
        annotation_num = len(f.readlines())
        return shape_num == annotation_num

    def on_draw_finished(self, shape_item: ShapeItem):
        label = ""
        if not shape_item.get_is_drawing_history():
            cus_message_box = AnnotationEnsureMessageBox(labels_color=self.labels_color,
                                                         last_label=self.last_selected_label, parent=self)
            if cus_message_box.exec():
                self.last_selected_label = label = cus_message_box.get_label()
                if not label:
                    InfoBar.error(
                        title='',
                        content=self.tr("Please select  or input a label "),
                        orient=Qt.Orientation.Vertical,
                        isClosable=True,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=-1,
                        parent=window_manager.find_window("main_widget")
                    )
                    self.canvas.scene.removeItem(shape_item)
                    return
        else:
            label = shape_item.get_annotation()
        if label:
            if not self.labels_color.get(label, None):
                self.labels_color.update({label: generate_random_color()})
                self.label_widget.set_labels(self.labels_color)
            color = self.labels_color[label]
            shape_item.set_color(color)
            shape_item.set_annotation(label)
            self.annotation_widget.add_annotation(shape_item.get_id(), label, color)
        self.canvas.scene.clearSelection()
        if not self.is_saved_annotation():
            self.image_list_widget.set_current_image_labeled(False)
        else:
            self.image_list_widget.set_current_image_labeled(True)

    def on_shape_item_selected_changed(self, uid: str):
        self.annotation_widget.set_selected_item(uid)

    def on_annotation_item_selected_changed(self, uid: str):
        self.canvas.set_shape_item_selected(uid)

    def on_annotation_item_edit_clicked(self, uid: str):
        cus_message_box = AnnotationEnsureMessageBox(labels_color=self.labels_color,
                                                     last_label="", parent=self)
        if cus_message_box.exec():
            label = cus_message_box.get_label()
            color = self.labels_color[label]
            self.annotation_widget.set_item_annotation(uid, label)
            self.annotation_widget.set_item_color(uid, color)
            shape_item = self.canvas.get_shape_item(uid)
            if shape_item:
                shape_item.set_color(color)
                shape_item.set_annotation(label)

    def update_label_file(self):
        if not self.image_dir_path:
            return
        with open(self.image_dir_path.parent / "classes.txt", "w") as f:
            for label in self.labels_color.keys():
                f.write(f"{label}\n")

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
        elif status == 3:
            self.cb_label.action_pre_image.setEnabled(False)
            self.cb_label.action_next_image.setEnabled(False)

    def set_history_image_and_annotations(self, image_path: Path):
        if not self.annotation_dir_path:
            return
        annotation_path = self.annotation_dir_path / (image_path.stem + ".txt")
        annotations = []
        if annotation_path.exists():
            with annotation_path.open("r") as f:
                for line in f.readlines():
                    annotation_data = line.strip().split(" ")
                    annotation = [float(x) for x in annotation_data]
                    annotations.append(annotation)
        self.annotation_widget.clear()
        self.canvas.set_image_and_draw_annotations(image_path, annotations, self.model_type, self.labels_color)

    def on_image_item_changed(self, image_path: str | Path):
        if isinstance(image_path, str):
            image_path = Path(image_path)
        self.set_history_image_and_annotations(image_path)

    def on_save_current_annotation(self):
        self.save_current_annotation()

    def on_delete_image_clicked(self):
        w = Dialog(self.tr("Warning"),
                   self.tr("Completely delete local data? Clicking [Yes] will delete the local data, "
                           "and clicking [No] will ignore the image"), self)
        w.yesButton.setText(self.tr("Yes"))
        w.cancelButton.setText(self.tr("No"))
        if w.exec():
            self.image_list_widget.delete_current_image_item()
            image_path = Path(self.image_list_widget.get_current_image_labeled()[0])
            if image_path.exists():
                image_path.unlink()
        else:
            self.image_list_widget.delete_current_image_item()

    def on_pre_image_clicked(self):
        _, labeled = self.image_list_widget.get_current_image_labeled()
        if not labeled:
            w = Dialog(self.tr("Warning"),
                       self.tr("Current annotation is not saved. Do you want to save it?"), self)
            w.yesButton.setText(self.tr("Save"))
            if w.exec():
                self.save_current_annotation()
                self.image_list_widget.set_current_image_labeled(True)
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
            else:
                return
        self.image_list_widget.next_item()

    def on_shape_clicked(self, shape_type: ShapeType):
        self.canvas.set_shape_type(shape_type)
        self.canvas.set_drawing_status(DrawingStatus.Draw)

    def set_annotation_task_id(self, annotation_task_id: str):
        self.annotation_task_id = annotation_task_id
        self.update_widget()

    def on_annotation_directory_changed(self, annotation_path: Path):
        self.annotation_dir_path = annotation_path
        db_update_annotation_dir_path(self.annotation_task_id, annotation_path.resolve().as_posix())
        self.update_widget()

    def set_image_path(self, image_path: Path):
        if not image_path.exists():
            InfoBar.error(
                title='',
                content=self.tr("Image path is not existed "),
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=window_manager.find_window("main_widget")
            )
            return
        if image_path == self.image_dir_path:
            return
        if image_path.is_file() and is_image(image_path):
            self.set_history_image_and_annotations(image_path)
            self.image_dir_path = image_path.parent
            self.cb_label.action_pre_image.setEnabled(False)
            self.cb_label.action_next_image.setEnabled(False)
        elif image_path.is_dir():
            self.image_dir_path = image_path
            self.label_widget.clear()
            self.canvas.clear()
            self.annotation_widget.clear()
            self.image_list_widget.clear()
            label_file_path = image_path.parent / "classes.txt"
            if label_file_path.exists():
                labels = open(label_file_path).read().splitlines()
                self.labels_color = {label: generate_random_color() for label in labels}
                self.label_widget.set_labels(self.labels_color)
            annotation_list = []
            if self.annotation_dir_path and self.annotation_dir_path.exists():
                for annotation in self.annotation_dir_path.iterdir():
                    annotation_list.append(annotation.stem)
            image_path_list = []
            for image_path in image_path.iterdir():
                if image_path.suffix in [".jpg", ".png", ".jpeg"]:
                    image_path_list.append(image_path)
            self.image_list_widget.set_image_dir_path(image_path_list, annotation_list)
            if len(image_path_list) > 0:
                self.cb_label.action_save_image.setEnabled(True)
                self.cb_label.action_delete.setEnabled(True)
            else:
                self.cb_label.action_save_image.setEnabled(False)
                self.cb_label.action_delete.setEnabled(False)
            self.label_widget.cus_add_label.setEnabled(True)

    def save_current_annotation(self):
        if self.image_dir_path and self.image_dir_path.exists():
            if not self.annotation_dir_path or not self.annotation_dir_path.exists():
                w = Dialog(self.tr("Warning"),
                           self.tr("annotation directory is ot existed, Create it?"), self)
                w.yesButton.setText(self.tr("Yes"))
                w.cancelButton.setText(self.tr("No"))
                if w.exec():
                    self.annotation_dir_path = self.image_dir_path.parent / "annotations"
                    self.annotation_dir_path.mkdir(exist_ok=True)
                    db_update_annotation_dir_path(self.annotation_task_id,
                                                  self.annotation_dir_path.resolve().as_posix())
                else:
                    return
        self.update_label_file()
        annotation_name = Path(self.image_list_widget.get_current_image_labeled()[0])
        annotation_path = self.annotation_dir_path / (annotation_name.stem + ".txt")
        annotations = []
        pix = self.canvas.get_background_pix()
        w, h = pix.width(), pix.height()
        for item in self.canvas.get_shape_items():
            if isinstance(item, ShapeItem):
                annotation = str(list(self.labels_color.keys()).index(item.get_annotation()))
                shape_data = item.get_shape_data()
                for index, data in enumerate(shape_data):
                    if index % 2 == 0:
                        data /= w
                    else:
                        data /= h
                    annotation += f" {data:.4f}"
                annotation += "\n"
                annotations.append(annotation)
        with open(annotation_path, "w", encoding="utf8") as f:
            f.writelines(annotations)
        self.image_list_widget.set_current_image_labeled(True)
        InfoBar.success(
            title='',
            content=self.tr("Annotations save successfully!"),
            orient=Qt.Orientation.Vertical,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=window_manager.find_window("main_widget")
        )
