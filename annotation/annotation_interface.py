from pathlib import Path

from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QVBoxLayout, QFileDialog
from qfluentwidgets import CommandBar, FluentIcon, Action
from loguru import logger
from annotation.canvas import InteractiveCanvas
from annotation.shape import ShapeType
from common.component.custom_icon import CustomFluentIcon

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
        self.cb = CommandBar()
        self.cb.setButtonTight(True)

        self.canvas = InteractiveCanvas()
        self.action_openfile = Action(CustomFluentIcon.FILE, self.tr("Open file"))
        self.action_openfile.triggered.connect(self.on_open_file)
        self.action_open_directory = Action(FluentIcon.FOLDER, self.tr("Open directory"))
        self.action_save_image = Action(FluentIcon.SAVE, self.tr("Save"))
        self.action_delete = Action(FluentIcon.DELETE, self.tr("Delete"))

        self.action_pre_image = Action(FluentIcon.LEFT_ARROW, self.tr("Prev"))
        self.action_next_image = Action(FluentIcon.RIGHT_ARROW, self.tr("Next"))

        # 鼠标指针
        self.action_select = Action(CustomFluentIcon.MOUSE_POINTER, self.tr("Select"))
        self.action_select.setCheckable(True)
        self.action_select.setChecked(True)
        # 编辑
        self.action_edit = Action(FluentIcon.EDIT, self.tr("Edit"))
        self.action_edit.setCheckable(True)
        # 多边形
        self.action_polygon = Action(CustomFluentIcon.POLYGON, self.tr("Polygon"))
        self.action_polygon.setCheckable(True)
        self.action_polygon.toggled.connect(self.on_select_polygon)
        # 矩形
        self.action_rectangle = Action(CustomFluentIcon.DETECT, self.tr("Rectangle"))
        self.action_rectangle.setCheckable(True)
        self.action_rectangle.toggled.connect(self.on_select_rectangle)
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
        self.action_group.addAction(self.action_edit)
        self.action_group.addAction(self.action_rectangle)
        self.action_group.addAction(self.action_polygon)
        self.action_group.addAction(self.action_circle)
        self.action_group.addAction(self.action_point)
        self.action_group.addAction(self.action_line)
        self.action_group.setExclusive(True)

        # 放大
        self.action_zoom_in = Action(FluentIcon.ZOOM_IN, self.tr("Zoom in"))
        self.action_zoom_in.triggered.connect(self.canvas.scale_up)
        # 缩小
        self.action_zoom_out = Action(FluentIcon.ZOOM_OUT, self.tr("Zoom out"))
        self.action_zoom_out.triggered.connect(self.canvas.scale_down)
        self.cb.addActions([
            self.action_openfile,
            self.action_open_directory,
            self.action_save_image,
            self.action_delete,
        ])
        self.cb.addSeparator()
        self.cb.addActions([
            self.action_pre_image,
            self.action_next_image
        ])
        self.cb.addSeparator()

        self.cb.addActions([
            self.action_select,
            self.action_edit,
            self.action_rectangle,
            self.action_polygon,
            self.action_circle,
            self.action_point,
            self.action_line
        ])

        self.cb.addSeparator()
        self.cb.addActions([

            self.action_zoom_in,
            self.action_zoom_out
        ])

        self.vly.addWidget(self.cb)
        self.vly.addWidget(self.canvas)
        # self.vly.addStretch(1)

        self._cur_file_path: Path | None = None
        self._cur_directory_path: Path | None = None

    def on_select_polygon(self, toggled: bool):
        if toggled:
            self.canvas.set_shape_type(ShapeType.Polygon)

    def on_select_rectangle(self, toggled):
        if toggled:
            self.canvas.set_shape_type(ShapeType.Rectangle)

    def on_select_circle(self, toggled):
        if toggled:
            self.canvas.set_shape_type(ShapeType.Circle)

    def on_select_point(self, toggled):
        if toggled:
            self.canvas.set_shape_type(ShapeType.Point)

    def on_select_line(self, toggled):
        if toggled:
            self.canvas.set_shape_type(ShapeType.Line)

    def on_open_file(self):
        if self._cur_file_path:
            if self._cur_file_path.is_file():
                _dir = self._cur_file_path.parent.resolve().as_posix()
            else:
                _dir = Path(".").as_posix()
        else:
            _dir = Path(".").as_posix()
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("Select a file"), _dir,
                                                  "All Files (*);;Image Files (*.jpg *.jpeg *.png *.bmp)")
        self._cur_file_path = Path(filename)
        if is_image(self._cur_file_path):
            self.canvas.set_image(self._cur_file_path)
        else:
            logger.warning(self.tr("Please select a correct image file"))

    def on_open_directory(self):
        if self._cur_directory_path:
            _dir = Path(self._cur_directory_path).resolve().as_posix()
        else:
            _dir = Path(".").as_posix()
        directory = QFileDialog.getExistingDirectory(self, self.tr("Select a directory"), _dir)
        if directory:
            self._cur_directory_path = Path(directory)
