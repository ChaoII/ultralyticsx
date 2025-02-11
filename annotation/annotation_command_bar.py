from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import CommandBar, FluentIcon, Action

from annotation.canvas_widget import DrawingStatus
from annotation.shape import ShapeType
from annotation.types import AlignmentType
from common.component.custom_icon import CustomFluentIcon


class AnnotationCommandBar(CommandBar):
    annotation_directory_changed = Signal(Path)

    save_annotation_clicked = Signal()
    delete_image_clicked = Signal()
    pre_image_clicked = Signal()
    next_image_clicked = Signal()

    drawing_status_selected = Signal(DrawingStatus)
    shape_selected = Signal(ShapeType)

    scale_down_clicked = Signal()
    scale_up_clicked = Signal()
    recover_clicked = Signal()

    align_type_clicked = Signal(AlignmentType)

    semi_automatic_annotation_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("LabelCommandBar")
        self.setButtonTight(True)

        self.action_annotation_directory = Action(FluentIcon.FOLDER, self.tr("Annotation directory"))
        self.action_annotation_directory.triggered.connect(self.on_select_directory)

        self.action_save_image = Action(FluentIcon.SAVE, self.tr("Save"))
        self.action_save_image.setShortcut("Ctrl+S")
        self.action_save_image.setEnabled(False)
        self.action_save_image.triggered.connect(self.on_save_annotation_clicked)
        self.action_delete = Action(FluentIcon.DELETE, self.tr("Delete"))
        self.action_delete.setEnabled(False)
        self.action_delete.triggered.connect(self.on_delete_image_clicked)
        self.action_pre_image = Action(FluentIcon.LEFT_ARROW, self.tr("Prev"))
        self.action_pre_image.triggered.connect(self.on_pre_image_clicked)
        self.action_pre_image.setEnabled(False)
        self.action_next_image = Action(FluentIcon.RIGHT_ARROW, self.tr("Next"))
        self.action_next_image.triggered.connect(self.on_next_image_clicked)
        self.action_next_image.setEnabled(False)

        # 鼠标指针
        self.action_select = Action(CustomFluentIcon.MOUSE_POINTER, self.tr("Select"))
        self.action_select.setCheckable(True)
        self.action_select.setChecked(True)
        self.action_select.toggled.connect(self.on_select_select)

        # 矩形
        self.action_rectangle = Action(CustomFluentIcon.DETECT, self.tr("Rectangle"))
        self.action_rectangle.setCheckable(True)
        self.action_rectangle.toggled.connect(self.on_select_rectangle)

        # 旋转矩形
        self.action_rotated_rectangle = Action(CustomFluentIcon.OBB, self.tr("Rotate rectangle"))
        self.action_rotated_rectangle.setCheckable(True)
        self.action_rotated_rectangle.toggled.connect(self.on_select_rotated_rectangle)

        # 多边形
        self.action_polygon = Action(CustomFluentIcon.POLYGON, self.tr("Polygon"))
        self.action_polygon.setCheckable(True)
        self.action_polygon.toggled.connect(self.on_select_polygon)

        # 圆形
        self.action_circle = Action(CustomFluentIcon.CIRCLE, self.tr("Circle"))
        self.action_circle.setCheckable(True)
        self.action_circle.toggled.connect(self.on_select_circle)
        # 点
        self.action_point = Action(CustomFluentIcon.POINT, self.tr("Point"))
        self.action_point.setCheckable(True)
        self.action_point.toggled.connect(self.on_select_point)
        # 线
        self.action_line = Action(CustomFluentIcon.LINE, self.tr("Line"))
        self.action_line.setCheckable(True)
        self.action_line.toggled.connect(self.on_select_line)

        self.action_group = QActionGroup(self)
        self.action_group.addAction(self.action_select)
        self.action_group.addAction(self.action_rectangle)
        self.action_group.addAction(self.action_rotated_rectangle)
        self.action_group.addAction(self.action_polygon)
        self.action_group.addAction(self.action_circle)
        self.action_group.addAction(self.action_point)
        self.action_group.addAction(self.action_line)
        self.action_group.setExclusive(True)

        # 放大
        self.action_zoom_in = Action(FluentIcon.ZOOM_IN, self.tr("Zoom in"))
        self.action_zoom_in.triggered.connect(lambda: self.scale_up_clicked.emit())
        # 缩小
        self.action_zoom_out = Action(FluentIcon.ZOOM_OUT, self.tr("Zoom out"))
        self.action_zoom_out.triggered.connect(lambda: self.scale_down_clicked.emit())
        # 恢复
        self.action_recover = Action(CustomFluentIcon.RECOVER, self.tr("recover"))
        self.action_recover.triggered.connect(lambda: self.recover_clicked.emit())

        self.action_align_left = Action(CustomFluentIcon.ALIGN_LEFT, self.tr("Align left"))
        self.action_align_left.triggered.connect(lambda: self.align_type_clicked.emit(AlignmentType.AlignLeft))
        self.action_align_right = Action(CustomFluentIcon.ALIGN_RIGHT, self.tr("Align right"))
        self.action_align_right.triggered.connect(lambda: self.align_type_clicked.emit(AlignmentType.AlignRight))
        self.action_align_top = Action(CustomFluentIcon.ALIGN_TOP, self.tr("Align top"))
        self.action_align_top.triggered.connect(lambda: self.align_type_clicked.emit(AlignmentType.AlignTop))
        self.action_align_bottom = Action(CustomFluentIcon.ALIGN_BOTTOM, self.tr("Align bottom"))
        self.action_align_bottom.triggered.connect(lambda: self.align_type_clicked.emit(AlignmentType.AlignBottom))
        self.action_align_horizontal_center = Action(CustomFluentIcon.ALIGN_HORIZONTAL_CENTER,
                                                     self.tr("Align horizontal center"))
        self.action_align_horizontal_center.triggered.connect(
            lambda: self.align_type_clicked.emit(AlignmentType.AlignHorizontalCenter))
        self.action_align_vertical_center = Action(CustomFluentIcon.ALIGN_VERTICAL_CENTER,
                                                   self.tr("Align vertical center"))
        self.action_align_vertical_center.triggered.connect(
            lambda: self.align_type_clicked.emit(AlignmentType.AlignVerticalCenter))
        self.action_align_horizontal_distribution = Action(CustomFluentIcon.ALIGN_HORIZONTAL_DISTRIBUTION,
                                                           self.tr("horizontal distribution"))
        self.action_align_horizontal_distribution.triggered.connect(
            lambda: self.align_type_clicked.emit(AlignmentType.AlignHorizontalDistribution))
        self.action_align_vertical_distribution = Action(CustomFluentIcon.ALIGN_VERTICAL_DISTRIBUTION,
                                                         self.tr("vertical distribution"))
        self.action_align_vertical_distribution.triggered.connect(
            lambda: self.align_type_clicked.emit(AlignmentType.AlignVerticalDistribution))

        self.action_semi_automatic_annotation = Action(CustomFluentIcon.SemiAutomatic,
                                                       self.tr("Semi automatic annotation"))
        self.action_semi_automatic_annotation.triggered.connect(lambda: self.semi_automatic_annotation_clicked.emit())

        self.addActions([
            self.action_annotation_directory,
            self.action_save_image,
            self.action_delete,
        ])
        self.addSeparator()
        self.addActions([
            self.action_pre_image,
            self.action_next_image
        ])
        self.addSeparator()

        self.addActions([
            self.action_select,
            self.action_rectangle,
            self.action_rotated_rectangle,
            self.action_polygon,
            self.action_circle,
            self.action_point,
            self.action_line
        ])

        self.addSeparator()
        self.addActions([
            self.action_zoom_in,
            self.action_zoom_out,
            self.action_recover
        ])

        self.addSeparator()
        self.addActions(
            [
                self.action_align_left,
                self.action_align_right,
                self.action_align_top,
                self.action_align_bottom,
                self.action_align_horizontal_center,
                self.action_align_vertical_center,
                self.action_align_horizontal_distribution,
                self.action_align_vertical_distribution
            ]
        )
        self.addSeparator()
        self.addAction(self.action_semi_automatic_annotation)
        self._cur_file_path: Path | None = None
        self._cur_directory_path: Path | None = None
        self.set_alignment_enabled(False)

    def on_pre_image_clicked(self):
        self.pre_image_clicked.emit()

    def on_next_image_clicked(self):
        self.next_image_clicked.emit()

    def on_save_annotation_clicked(self):
        self.save_annotation_clicked.emit()

    def on_delete_image_clicked(self):
        self.delete_image_clicked.emit()

    def on_select_select(self, toggled: bool):
        if toggled:
            self.drawing_status_selected.emit(DrawingStatus.Select)

    def on_select_rectangle(self, toggled):
        if toggled:
            self.shape_selected.emit(ShapeType.Rectangle)

    def on_select_rotated_rectangle(self, toggled):
        if toggled:
            self.shape_selected.emit(ShapeType.RotatedRectangle)

    def on_select_polygon(self, toggled: bool):
        if toggled:
            self.shape_selected.emit(ShapeType.Polygon)

    def on_select_circle(self, toggled):
        if toggled:
            self.shape_selected.emit(ShapeType.Circle)

    def on_select_point(self, toggled):
        if toggled:
            self.shape_selected.emit(ShapeType.Point)

    def on_select_line(self, toggled):
        if toggled:
            self.shape_selected.emit(ShapeType.Line)

    def on_select_directory(self):
        if self._cur_directory_path:
            _dir = Path(self._cur_directory_path).resolve().as_posix()
        else:
            _dir = Path(".").as_posix()
        directory = QFileDialog.getExistingDirectory(self, self.tr("Select a directory"), _dir)
        if directory:
            self._cur_directory_path = Path(directory)
            self.annotation_directory_changed.emit(self._cur_directory_path)

    def set_shape_enabled(self, enabled: bool):
        self.action_rectangle.setEnabled(enabled)
        self.action_rotated_rectangle.setEnabled(enabled)
        self.action_polygon.setEnabled(enabled)
        self.action_circle.setEnabled(enabled)
        self.action_point.setEnabled(enabled)
        self.action_line.setEnabled(enabled)

    def set_alignment_enabled(self, enabled: bool):
        self.action_align_left.setEnabled(enabled)
        self.action_align_right.setEnabled(enabled)
        self.action_align_top.setEnabled(enabled)
        self.action_align_bottom.setEnabled(enabled)
        self.action_align_horizontal_center.setEnabled(enabled)
        self.action_align_vertical_center.setEnabled(enabled)
        self.action_align_horizontal_distribution.setEnabled(enabled)
        self.action_align_vertical_distribution.setEnabled(enabled)
