from typing import Optional

from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, ComboBox, CompactSpinBox, SwitchButton, \
    PrimaryPushButton, StateToolTip, \
    InfoBar, InfoBarPosition, ToolTipFilter, ToolTipPosition

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_icon import CustomFluentIcon
from common.file_select_widget import FileSelectWidget
from ..model_trainer_thread.model_export_thread import ModelExportThread
from ...types import TaskInfo


class FixWidthBodyLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(100)
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))


class ModelExportWidget(CollapsibleWidgetItem):
    export_model_finished = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(self.tr("▌Model export"), parent=parent)
        # ------------------------训练参数-------------------------

        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setFixedWidth(300)

        self.cmb_model_format = ComboBox()
        self.cmb_model_format.setFixedWidth(300)
        self.cmb_model_format.addItems(
            ['torchscript', 'onnx', 'openvino', 'engine', 'coreml', 'saved_model', 'pb', 'tflite', 'edgetpu', 'tfjs',
             'paddle', 'ncnn'])

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

        self.fly_export_setting1 = QFormLayout()
        self.fly_export_setting1.setVerticalSpacing(15)
        self.fly_export_setting1.setHorizontalSpacing(40)
        self.fly_export_setting1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_export_setting2 = QFormLayout()
        self.fly_export_setting2.setVerticalSpacing(15)
        self.fly_export_setting2.setHorizontalSpacing(40)
        self.fly_export_setting2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_export_setting1.addRow(FixWidthBodyLabel(self.tr("model name: "), self), self.cmb_model_name)
        self.fly_export_setting1.addRow(FixWidthBodyLabel(self.tr("keras: "), self), self.btn_keras)
        self.fly_export_setting1.addRow(FixWidthBodyLabel(self.tr("optimize: "), self), self.btn_optimize)
        self.fly_export_setting1.addRow(FixWidthBodyLabel(self.tr("int8: "), self), self.btn_int8)
        self.fly_export_setting1.addRow(FixWidthBodyLabel(self.tr("dynamic: "), self), self.btn_dynamic)

        self.fly_export_setting2.addRow(FixWidthBodyLabel(self.tr("model_format: "), self), self.cmb_model_format)
        self.fly_export_setting2.addRow(FixWidthBodyLabel(self.tr("simplify: "), self), self.btn_simplify)
        self.fly_export_setting2.addRow(FixWidthBodyLabel(self.tr("opset: "), self), self.spb_opset)
        self.fly_export_setting2.addRow(FixWidthBodyLabel(self.tr("trt_workspace: "), self), self.spb_trt_workspace)
        self.fly_export_setting2.addRow(FixWidthBodyLabel(self.tr("nms: "), self), self.btn_nms)

        self.vly_export_setting = QVBoxLayout()
        self.vly_export_setting.setSpacing(15)
        self.vly_export_setting.setContentsMargins(20, 0, 20, 0)

        self.hly_export_setting = QHBoxLayout()
        self.hly_export_setting.setSpacing(40)
        self.hly_export_setting.addLayout(self.fly_export_setting1)
        self.hly_export_setting.addLayout(self.fly_export_setting2)
        self.hly_export_setting.addStretch(1)

        self.vly_export_setting.addLayout(self.hly_export_setting)

        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)

        self.vly_content = QVBoxLayout(self.content_widget)
        self.vly_content.setContentsMargins(20, 0, 20, 20)
        self.vly_content.setSpacing(30)

        self.vly_content.addLayout(self.vly_export_setting)

        self.btn_export = PrimaryPushButton(CustomFluentIcon.MODEL_EXPORT, self.tr("Export"))
        self.btn_export.setFixedWidth(120)
        self.fs_export_path = FileSelectWidget()
        self.fs_export_path.setMinimumWidth(450)
        self.fs_export_path.setVisible(False)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_export)
        self.hly_btn.addWidget(self.fs_export_path)
        self.hly_btn.addStretch(1)

        self.vly_content.addLayout(self.hly_btn)

        self.set_content_widget(self.content_widget)
        self._task_info: TaskInfo | None = None
        self._export_parameter = dict()
        self._state_tool_tip = None
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_export.clicked.connect(self._on_export_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
        self._init_model_name()

    def _init_model_name(self):
        self.cmb_model_name.clear()
        model_weight_path = self._task_info.task_dir / "weights"
        if not model_weight_path.exists():
            return
        for item in model_weight_path.iterdir():
            if item.is_file() and item.suffix == ".pt":
                self.cmb_model_name.addItem(item.name)
        self.cmb_model_name.setCurrentIndex(0)

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
        self.export_model_finished.emit(False)
        self.btn_export.setEnabled(False)

    def _on_export_end(self):
        self.state_tool_tip.setContent(
            self.tr('Export Model completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
        self.export_model_finished.emit(True)
        self.btn_export.setEnabled(True)
        # self.fs_export_path.setText(self._task_info.task_dir / "weight")

    @Slot(str)
    def _on_export_failed(self, error_msg: str):
        if self._state_tool_tip:
            self.state_tool_tip.setState(True)
            self.state_tool_tip = None
            self.export_model_finished.emit(True)
            self.btn_export.setEnabled(True)
            InfoBar.error(
                title='',
                content=self.tr("Export model failed: ") + error_msg,
                orient=Qt.Orientation.Vertical,  # 内容太长时可使用垂直布局
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self.parent().parent()
            )

    def export(self):
        task_thread = self.create_export_thread()
        task_thread.start()

    def _on_export_clicked(self):
        parameter = dict(
            model_name=self._task_info.task_dir / "weights" / self.cmb_model_name.currentText(),
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
        self.state_tool_tip = StateToolTip(
            self.tr('Model is exporting '), self.tr('Please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()
