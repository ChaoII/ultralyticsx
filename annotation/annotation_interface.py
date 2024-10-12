from pathlib import Path

from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QVBoxLayout, QFileDialog, QHBoxLayout
from qfluentwidgets import CommandBar, FluentIcon, Action
from loguru import logger

from annotation.annotations_list_widget import AnnotationListWidget
from annotation.canvas_widget import InteractiveCanvas
from annotation.annotation_command_bar import AnnotationCommandBar
from annotation.image_list_widget import ImageListWidget
from annotation.labels_settings_widget import LabelSettingsWidget
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

        self.cb_label = AnnotationCommandBar(self)
        self.canvas = InteractiveCanvas()
        self.label_widget = LabelSettingsWidget()
        self.label_widget.set_labels(["张三", "李四", "王五", "赵六"])
        self.annotation_widget = AnnotationListWidget()
        self.image_list_widget = ImageListWidget()
        self.annotation_widget.add_annotation("嘟嘟")
        self.annotation_widget.add_annotation("猪猪")
        self.annotation_widget.add_annotation("鸭鸭")
        self.annotation_widget.add_annotation("狗蛋")

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

    def connect_signals_and_slots(self):
        self.cb_label.shape_selected.connect(lambda x: self.canvas.set_shape_type(x))
        self.cb_label.scale_down_clicked.connect(lambda: self.canvas.scale_down())
        self.cb_label.scale_up_clicked.connect(lambda: self.canvas.scale_up())
        self.cb_label.current_path_changed.connect(lambda x: self.canvas.set_image(x))
