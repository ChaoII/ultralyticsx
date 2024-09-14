import enum
from pathlib import Path
from typing import Optional

import yaml
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QWidget, QGridLayout, QFormLayout, QVBoxLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, ComboBox, themeColor, CompactSpinBox, CompactDoubleSpinBox, SwitchButton, \
    CheckBox, LineEdit, StrongBodyLabel, SubtitleLabel, PushButton, PrimaryPushButton, FluentIcon, StateToolTip, \
    InfoBar, InfoBarPosition, ToolTipFilter, ToolTipPosition
from sqlalchemy import and_

from common.collapsible_widget import CollapsibleWidgetItem, ToolBox
from common.custom_icon import CustomFluentIcon
from common.db_helper import db_session
from common.file_select_widget import FileSelectWidget
from common.model_type_widget import ModelType
from dataset.types import DatasetStatus
from home.options import model_type_list_map
from home.task.model_trainer_thread.model_export_thread import ModelExportThread
from home.types import TaskInfo, TaskStatus
from models.models import Dataset, Task


class FixWidthBodyLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(100)
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))


class ModelExportWidget(CollapsibleWidgetItem):
    export_model_finished = Signal(TaskInfo)

    def __init__(self, parent=None):
        super().__init__(self.tr("▌Model export"), parent=parent)
        # ------------------------训练参数-------------------------

        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setFixedWidth(300)
        self.cmb_model_name.addItems(["auto", "SGD", "Adam", "Adamax", "AdamW", "NAdam", "RAdam", "RMSProp"])

        self.cmb_model_format = ComboBox()
        self.cmb_model_format.setFixedWidth(300)
        self.cmb_model_format.addItems(["auto", "SGD", "Adam", "Adamax", "AdamW", "NAdam", "RAdam", "RMSProp"])

        self.btn_keras = SwitchButton()
        self.btn_keras.setChecked(False)
        self.btn_keras.setFixedHeight(33)

        self.btn_optimize = SwitchButton()
        self.btn_optimize.setChecked(False)
        self.btn_optimize.setFixedHeight(33)

        self.btn_int8 = SwitchButton()
        self.btn_int8.setChecked(False)
        self.btn_int8.setFixedHeight(33)

        self.btn_dynamic = SwitchButton()
        self.btn_dynamic.setChecked(False)
        self.btn_dynamic.setFixedHeight(33)

        self.btn_simplify = SwitchButton()
        self.btn_simplify.setChecked(False)
        self.btn_simplify.setFixedHeight(33)

        self.spb_opset = CompactSpinBox()
        self.spb_opset.setRange(7, 20)
        self.spb_opset.setValue(11)
        self.spb_opset.setFixedWidth(300)

        self.spb_trt_workspace = CompactSpinBox()
        self.spb_trt_workspace.setRange(1, 24)
        self.spb_trt_workspace.setValue(4)
        self.spb_trt_workspace.setFixedWidth(300)

        self.btn_nms = SwitchButton()
        self.btn_nms.setChecked(False)
        self.btn_nms.setFixedHeight(33)

        self.fly_train_setting1 = QFormLayout()
        self.fly_train_setting1.setVerticalSpacing(15)
        self.fly_train_setting1.setHorizontalSpacing(40)
        self.fly_train_setting1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_train_setting2 = QFormLayout()
        self.fly_train_setting2.setVerticalSpacing(15)
        self.fly_train_setting2.setHorizontalSpacing(40)
        self.fly_train_setting2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("model name: "), self), self.cmb_model_name)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("keras: "), self), self.btn_keras)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("optimize: "), self), self.btn_optimize)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("int8: "), self), self.btn_int8)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("dynamic: "), self), self.btn_dynamic)

        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("model_format: "), self), self.cmb_model_format)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("simplify: "), self), self.btn_simplify)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("opset: "), self), self.spb_opset)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("trt_workspace: "), self), self.spb_trt_workspace)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("nms: "), self), self.btn_nms)

        self.vly_export_setting = QVBoxLayout()
        self.vly_export_setting.setSpacing(15)
        self.vly_export_setting.setContentsMargins(20, 0, 20, 0)

        self.hly_train_setting = QHBoxLayout()
        self.hly_train_setting.setSpacing(40)
        self.hly_train_setting.addLayout(self.fly_train_setting1)
        self.hly_train_setting.addLayout(self.fly_train_setting2)
        self.hly_train_setting.addStretch(1)

        self.vly_export_setting.addLayout(self.hly_train_setting)

        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)

        self.vly_content = QVBoxLayout(self.content_widget)
        self.vly_content.setContentsMargins(20, 0, 20, 20)
        self.vly_content.setSpacing(30)

        self.vly_content.addLayout(self.vly_export_setting)

        self.btn_export = PrimaryPushButton(CustomFluentIcon.MODEL_EXPORT, self.tr("Export"))
        self.btn_export.setFixedWidth(120)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_export)
        self.hly_btn.addStretch(1)

        self.vly_content.addLayout(self.hly_btn)

        self.set_content_widget(self.content_widget)
        self._task_info: TaskInfo | None = None
        self._export_parameter = dict()
        self.stateTooltip = None
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_export.clicked.connect(self._on_export_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info

    def create_export_thread(self) -> Optional[ModelExportThread]:
        model_export_thread = ModelExportThread(self._export_parameter)
        model_export_thread.model_export_start.connect(self._on_export_start)
        model_export_thread.model_export_end.connect(self._on_export_end)
        model_export_thread.model_export_failed.connect(self._on_export_failed)

        if model_export_thread.init_model_exporter():
            return model_export_thread
        else:
            return None

    def _on_export_start(self):
        pass

    def _on_export_end(self):
        pass

    def _on_export_failed(self):
        pass

    def export(self):
        self.set_task_info(self._task_info)
        task_thread = self.create_export_thread()
        task_thread.start()

    def _on_export_clicked(self):
        parameter = dict(
            format=self.cmb_model_format.currentText(),
            keras=self.btn_keras.isChecked(),
            optimize=self.btn_optimize.isChecked(),
            int8=self.btn_int8.isChecked(),
            dynamic=self.btn_dynamic.isChecked(),
            simplify=self.btn_simplify.isChecked(),
            opset=self.spb_opset.value(),
            workspace=self.spb_trt_workspace.value(),
            nms=self.btn_nms.isChecked()
        )
        self._export_parameter = parameter
        self.export()
