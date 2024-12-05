from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QPointF
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import Dialog, InfoBar, InfoBarPosition, SimpleCardWidget

from annotation.annotation_command_bar import AnnotationCommandBar
from annotation.annotation_ensure_message_box import AnnotationEnsureMessageBox
from annotation.annotations_list_widget import AnnotationListWidget
from annotation.canvas_widget import InteractiveCanvas, DrawingStatus
from annotation.image_list_widget import ImageListWidget
from annotation.item_property_widget import RectItemPropertyWidget
from annotation.labels_settings_widget import LabelSettingsWidget
from annotation.semi_annotation_widget import SemiAutomaticAnnotationEnsureMessageBox, ModelPredict
from annotation.shape import ShapeType, ShapeItem
from annotation.types import AnnotationStatus
from common.component.custom_icon import CustomFluentIcon
from common.component.fill_tool_button import FillToolButton
from common.component.model_type_widget import ModelType
from common.core.content_widget_base import ContentWidgetBase
from common.core.window_manager import window_manager
from common.database.annotation_task_helper import db_update_annotation_dir_path
from common.database.db_helper import db_session
from common.utils.utils import is_image, generate_random_color, format_time_delta
from models.models import AnnotationTask


class LabelPropertyWidget(SimpleCardWidget):

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.label_widget = LabelSettingsWidget()
        self.annotation_widget = AnnotationListWidget()
        self.image_list_widget = ImageListWidget()
        self.vly_right = QVBoxLayout(self)
        self.vly_right.setContentsMargins(0, 0, 0, 0)
        self.vly_right.addWidget(self.label_widget)
        self.vly_right.addWidget(self.annotation_widget)
        self.vly_right.addWidget(self.image_list_widget)
        self.animation = QPropertyAnimation(self, b"width_")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.BezierSpline)
        self.is_collapse = False

    @Property(int)
    def width_(self):
        return self.width()

    @width_.setter
    def width_(self, value):
        self.setFixedWidth(value)

    def on_btn_collapse_clicked(self):
        if self.width() == 0:
            self.animation.setStartValue(0)
            self.animation.setEndValue(200)
            self.is_collapse = False
        else:
            self.animation.setStartValue(200)
            self.animation.setEndValue(0)
            self.is_collapse = True
        self.animation.start()


class AnnotationWidget(ContentWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("annotation_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setContentsMargins(10, 10, 10, 10)
        self.vly.setSpacing(4)

        self.cb_label = AnnotationCommandBar(self)
        self.canvas = InteractiveCanvas()

        self.btn_item_property = FillToolButton(CustomFluentIcon.EXPAND_RIGHT)
        self.btn_item_property.set_border_radius(0)
        self.btn_item_property.setFixedSize(30, 30)
        self.btn_item_property.setParent(self.canvas)

        self.btn_label_property = FillToolButton(CustomFluentIcon.COLLAPSE_LEFT)
        self.btn_label_property.set_border_radius(0)
        self.btn_label_property.setFixedSize(30, 30)
        self.btn_label_property.setParent(self.canvas)
        self.label_property_widget = LabelPropertyWidget()
        self.item_property_widget = RectItemPropertyWidget()

        # self.vly_right.addStretch(1)
        self.hly = QHBoxLayout()
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.hly.setSpacing(0)
        self.hly.addWidget(self.label_property_widget)
        self.hly.addWidget(self.canvas)
        self.hly.addWidget(self.item_property_widget)
        self.vly.addWidget(self.cb_label)
        self.vly.addLayout(self.hly)
        self.connect_signals_and_slots()
        self.image_dir_path: Path | None = None
        self.annotation_dir_path: Path | None = None
        self.labels_color: dict[str, QColor] = dict()
        self.annotation_task_id = ""
        self.model_type = ModelType.DETECT
        self.last_selected_label = ""

    def connect_signals_and_slots(self):
        self.btn_item_property.clicked.connect(self.on_btn_item_clicked)
        self.btn_label_property.clicked.connect(self.on_btn_label_clicked)

        self.cb_label.annotation_directory_changed.connect(self.on_annotation_directory_changed)
        self.cb_label.save_annotation_clicked.connect(self.save_current_annotation)
        self.cb_label.delete_image_clicked.connect(self.on_delete_image_clicked)
        self.cb_label.pre_image_clicked.connect(self.on_pre_image_clicked)
        self.cb_label.next_image_clicked.connect(self.on_next_image_clicked)
        self.cb_label.shape_selected.connect(self.on_shape_clicked)
        self.cb_label.drawing_status_selected.connect(lambda x: self.canvas.set_drawing_status(x))
        self.cb_label.scale_down_clicked.connect(lambda: self.canvas.scale_down())
        self.cb_label.scale_up_clicked.connect(lambda: self.canvas.scale_up())
        self.cb_label.recover_clicked.connect(lambda: self.canvas.reset_scale())
        self.cb_label.align_type_clicked.connect(lambda x: self.canvas.align_item(x))
        self.cb_label.semi_automatic_annotation_clicked.connect(self.on_semi_automatic_annotation_clicked)

        self.canvas.is_drawing_changed.connect(self.on_is_drawing_changed)
        self.canvas.draw_finished.connect(self.on_draw_finished)
        self.canvas.shape_item_selected_changed.connect(self.on_shape_item_selected_changed)
        self.canvas.shape_item_geometry_changed.connect(self.on_shape_item_geometry_changed)
        self.canvas.delete_shape_item_clicked.connect(
            lambda x: self.label_property_widget.annotation_widget.delete_annotation_item(x))
        self.canvas.width_changed.connect(self.on_canvas_width_changed)

        self.label_property_widget.label_widget.add_label_clicked.connect(self.on_add_label)
        self.label_property_widget.label_widget.delete_label_clicked.connect(self.on_delete_label)
        self.label_property_widget.label_widget.label_item_color_changed.connect(self.on_label_item_color_changed)

        self.label_property_widget.annotation_widget.delete_annotation_clicked.connect(
            lambda x: self.canvas.delete_shape_item(x))
        self.label_property_widget.annotation_widget.edit_annotation_clicked.connect(
            self.on_annotation_item_edit_clicked)
        self.label_property_widget.annotation_widget.annotation_item_selected_changed.connect(
            self.on_annotation_item_selected_changed)

        self.label_property_widget.image_list_widget.image_item_changed.connect(self.on_image_item_changed)
        self.label_property_widget.image_list_widget.item_ending_status_changed.connect(self.on_move_ending_status)
        self.label_property_widget.image_list_widget.save_annotation_clicked.connect(
            lambda: self.save_current_annotation())

        self.item_property_widget.shape_changed.connect(self.on_shape_changed)

    def on_shape_changed(self, x, y, w, h):
        items = self.canvas.scene.selectedItems()
        if len(items) > 0:
            item = items[0]
            if isinstance(item, ShapeItem):
                item.update_points([QPointF(x, y), QPointF(x + w, y + h)])
                item.update()

    def on_shape_item_selected_changed(self, item_ids: list[str]):
        self.label_property_widget.annotation_widget.set_selected_item(item_ids)
        self.update_item_property(item_ids)
        if len(item_ids) >= 2:
            self.cb_label.set_alignment_enabled(True)
        else:
            self.cb_label.set_alignment_enabled(False)

    def on_shape_item_geometry_changed(self, shape_data: list):
        self.update_item_property(shape_data)

    def on_btn_item_clicked(self):
        self.item_property_widget.on_btn_collapse_clicked()
        if self.item_property_widget.is_collapse:
            self.btn_item_property.set_icon(CustomFluentIcon.EXPAND_RIGHT)
        else:
            self.btn_item_property.set_icon(CustomFluentIcon.COLLAPSE_RIGHT)

    def on_btn_label_clicked(self):
        self.label_property_widget.on_btn_collapse_clicked()
        if self.label_property_widget.is_collapse:
            self.btn_label_property.set_icon(CustomFluentIcon.EXPAND_LEFT)
        else:
            self.btn_label_property.set_icon(CustomFluentIcon.COLLAPSE_LEFT)

    def on_canvas_width_changed(self, _):
        self.btn_item_property.move(self.canvas.width() - self.btn_item_property.width(), 0)
        self.btn_label_property.move(0, 0)

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
        self.label_property_widget.label_widget.set_labels(self.labels_color)
        self.update_label_file()

    def on_delete_label(self, label: str):
        self.labels_color.pop(label)
        self.label_property_widget.label_widget.set_labels(self.labels_color)
        self.label_property_widget.annotation_widget.delete_annotation_item_by_annotation(label)
        self.update_label_file()

    def on_label_item_color_changed(self, label: str, color: QColor):
        self.labels_color[label] = color
        self.label_property_widget.annotation_widget.update_annotation_item_color(label, color)
        self.canvas.update_shape_item_color(label, color)

    def on_is_drawing_changed(self, is_drawing: bool):
        if is_drawing:
            self.cb_label.set_shape_enabled(False)
        else:
            self.update_shape_status()

    def is_saved_annotation(self) -> bool:
        shape_num = len(self.canvas.get_shape_items()) - 1
        image_path = Path(self.label_property_widget.image_list_widget.get_current_image_labeled()[0])
        annotation_path = self.annotation_dir_path / (image_path.stem + ".txt")
        if not annotation_path.exists():
            return False
        with open(annotation_path, "r", encoding="utf-8") as f:
            annotation_num = len(f.readlines())
        return shape_num == annotation_num

    def on_semi_automatic_annotation_clicked(self):
        cus_message_box = SemiAutomaticAnnotationEnsureMessageBox(parent=self)
        if cus_message_box.exec():
            model_path = Path(cus_message_box.get_model_path())
            if not model_path.exists() or not model_path.is_file() or model_path.suffix != ".pt":
                InfoBar.error(
                    title="",
                    content=self.tr("Please select a correct model path"),
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT,
                    parent=window_manager.find_window("main_widget")
                )
                return
            predictor = ModelPredict(self)
            image_path = Path(self.label_property_widget.image_list_widget.get_current_image_labeled()[0])
            result = predictor.predict(model_path, image_path)
            annotation_path = self.annotation_dir_path / (image_path.stem + ".txt")
            annotations = []
            if self.model_type == ModelType.DETECT:
                boxes = result.boxes.data.cpu().tolist()
                for box in boxes:
                    x1, y1, x2, y2, conf, class_id = box
                    labels = list(self.labels_color.keys())
                    if class_id >= len(labels):
                        InfoBar.error(
                            title='',
                            content=self.tr("Labels error, please set enough label firstly"),
                            orient=Qt.Orientation.Vertical,
                            isClosable=True,
                            position=InfoBarPosition.TOP_RIGHT,
                            duration=-1,
                            parent=window_manager.find_window("main_widget")
                        )
                        return
                    pix = self.canvas.get_background_pix()
                    w, h = pix.width(), pix.height()
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1
                    annotation = f"{class_id} {x_center / w:.4f} {y_center / h:.4f} {width / w:.4f} {height / h:.4f}\n"
                    annotations.append(annotation)
            else:
                raise NotImplementedError("semi-automatic annotation only support detection task")
            with open(annotation_path, "w", encoding="utf8") as f:
                f.writelines(annotations)
            self.label_property_widget.image_list_widget.set_current_image_labeled(True)
            self.set_history_image_and_annotations(image_path)

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
                self.label_property_widget.label_widget.set_labels(self.labels_color)
            color = self.labels_color[label]
            shape_item.set_color(color)
            shape_item.set_annotation(label)
            self.label_property_widget.annotation_widget.add_annotation(shape_item.get_id(), label, color)
        self.canvas.scene.clearSelection()
        if not self.is_saved_annotation():
            self.label_property_widget.image_list_widget.set_current_image_labeled(False)
        else:
            self.label_property_widget.image_list_widget.set_current_image_labeled(True)

    def update_item_property(self, item_ids: list[str]):
        if len(item_ids) > 0:
            item_id = item_ids[0]
            item = self.canvas.get_shape_item(item_id)
            if isinstance(item, ShapeItem):
                self.item_property_widget.set_id(str(item_id))
                self.item_property_widget.set_annotation(item.get_annotation())
                self.item_property_widget.update_property(item.get_shape_data())

    def on_annotation_item_selected_changed(self, item_ids: list[str]):
        self.canvas.set_shape_item_selected(item_ids)
        self.update_item_property(item_ids)

    def on_annotation_item_edit_clicked(self, item_id: str):
        cus_message_box = AnnotationEnsureMessageBox(labels_color=self.labels_color,
                                                     last_label="", parent=self)
        if cus_message_box.exec():
            label = cus_message_box.get_label()
            color = self.labels_color[label]
            self.label_property_widget.annotation_widget.set_item_annotation(item_id, label)
            self.label_property_widget.annotation_widget.set_item_color(item_id, color)
            shape_item = self.canvas.get_shape_item(item_id)
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
        self.label_property_widget.annotation_widget.clear()
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
            self.label_property_widget.image_list_widget.delete_current_image_item()
            image_path = Path(self.label_property_widget.image_list_widget.get_current_image_labeled()[0])
            if image_path.exists():
                image_path.unlink()
        else:
            self.label_property_widget.image_list_widget.delete_current_image_item()

    def on_pre_image_clicked(self):
        _, labeled = self.label_property_widget.image_list_widget.get_current_image_labeled()
        if not labeled:
            w = Dialog(self.tr("Warning"),
                       self.tr("Current annotation is not saved. Do you want to save it?"), self)
            w.yesButton.setText(self.tr("Save"))
            if w.exec():
                self.save_current_annotation()
                self.label_property_widget.image_list_widget.set_current_image_labeled(True)
            else:
                return
        self.label_property_widget.image_list_widget.pre_item()

    def on_next_image_clicked(self):
        _, labeled = self.label_property_widget.image_list_widget.get_current_image_labeled()
        if not labeled:
            w = Dialog(self.tr("Warning"),
                       self.tr("Current annotation is not saved. Do you want to save it?"), self)
            w.yesButton.setText(self.tr("Save"))
            if w.exec():
                self.save_current_annotation()
            else:
                return
        self.label_property_widget.image_list_widget.next_item()

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
            self.label_property_widget.label_widget.clear()
            self.canvas.clear()
            self.label_property_widget.annotation_widget.clear()
            self.label_property_widget.image_list_widget.clear()
            label_file_path = image_path.parent / "classes.txt"
            if label_file_path.exists():
                labels = open(label_file_path).read().splitlines()
                self.labels_color = {label: generate_random_color() for label in labels}
                self.label_property_widget.label_widget.set_labels(self.labels_color)
            annotation_list = []
            if self.annotation_dir_path and self.annotation_dir_path.exists():
                for annotation in self.annotation_dir_path.iterdir():
                    annotation_list.append(annotation.stem)
            image_path_list = []
            for image_path in image_path.iterdir():
                if image_path.suffix in [".jpg", ".png", ".jpeg"]:
                    image_path_list.append(image_path)
            self.label_property_widget.image_list_widget.set_image_dir_path(image_path_list, annotation_list)
            if len(image_path_list) > 0:
                self.cb_label.action_save_image.setEnabled(True)
                self.cb_label.action_delete.setEnabled(True)
            else:
                self.cb_label.action_save_image.setEnabled(False)
                self.cb_label.action_delete.setEnabled(False)
            self.label_property_widget.label_widget.cus_add_label.setEnabled(True)

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
        annotation_name = Path(self.label_property_widget.image_list_widget.get_current_image_labeled()[0])
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
        self.label_property_widget.image_list_widget.set_current_image_labeled(True)
        labeled_count, total_count = self.label_property_widget.image_list_widget.get_all_image_labeled_count()
        with db_session() as session:
            task: AnnotationTask = session.query(AnnotationTask).filter_by(task_id=self.annotation_task_id).first()
            task.labeled_num = labeled_count
            task.total = total_count
            if labeled_count == total_count:
                task.task_status = AnnotationStatus.AnnoFinished.value
                task.end_time = datetime.now()
                delta = task.end_time - task.start_time
                task.elapsed = format_time_delta(delta)
            else:
                task.task_status = AnnotationStatus.Annotating.value
            InfoBar.success(
                title='',
                content=self.tr("Annotations save successfully!"),
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=window_manager.find_window("main_widget")
            )
