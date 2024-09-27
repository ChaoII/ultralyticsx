from pprint import pprint
from typing import Optional

from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, ComboBox, CompactSpinBox, SwitchButton, \
    PrimaryPushButton, StateToolTip, \
    InfoBar, InfoBarPosition, ToolTipFilter, ToolTipPosition, ImageLabel

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_icon import CustomFluentIcon
from common.file_select_widget import FileSelectWidget
from common.image_select_widget import ImageSelectWidget
from ..model_trainer_thread.model_predict_thread import ModelPredictorThread
from ...types import TaskInfo


class FixWidthBodyLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(100)
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))


class ModelPredictWidget(CollapsibleWidgetItem):
    export_model_finished = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(self.tr("▌Model predict"), parent=parent)
        # ------------------------训练参数-------------------------

        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setFixedWidth(300)

        self.cmb_model_format = ComboBox()
        self.cmb_model_format.setFixedWidth(300)
        self.cmb_model_format.addItems(
            ['torchscript', 'onnx', 'openvino', 'engine', 'coreml', 'saved_model', 'pb', 'tflite', 'edgetpu', 'tfjs',
             'paddle', 'ncnn'])

        self.hly_export_setting = QHBoxLayout()
        self.hly_export_setting.setSpacing(40)
        self.hly_export_setting.addWidget(FixWidthBodyLabel(self.tr("model name: ")))
        self.hly_export_setting.addWidget(self.cmb_model_name)
        self.hly_export_setting.addWidget(FixWidthBodyLabel(self.tr("model_format: ")))
        self.hly_export_setting.addWidget(self.cmb_model_format)
        self.hly_export_setting.addStretch(1)

        self.lbl_input_image = ImageSelectWidget()
        self.lbl_input_image.setFixedSize(300, 400)
        self.lbl_input_image.set_border_radius(10, 10, 10, 10)
        self.lbl_output_image = ImageLabel()
        self.lbl_input_image.setFixedSize(300, 400)
        self.hly_images = QHBoxLayout()
        self.hly_images.addWidget(self.lbl_input_image)
        self.hly_images.addWidget(self.lbl_output_image)

        self.vly_export_setting = QVBoxLayout()
        self.vly_export_setting.setSpacing(15)
        self.vly_export_setting.setContentsMargins(20, 0, 20, 0)
        self.vly_export_setting.addLayout(self.hly_export_setting)
        self.vly_export_setting.addLayout(self.hly_images)

        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)

        self.vly_content = QVBoxLayout(self.content_widget)
        self.vly_content.setContentsMargins(20, 0, 20, 20)
        self.vly_content.setSpacing(30)
        self.vly_content.addLayout(self.vly_export_setting)

        self.btn_predict = PrimaryPushButton(CustomFluentIcon.MODEL_EXPORT, self.tr("Predict"))
        self.btn_predict.setFixedWidth(120)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_predict)
        self.hly_btn.addStretch(1)
        self.vly_content.addLayout(self.hly_btn)

        self.set_content_widget(self.content_widget)
        self._task_info: TaskInfo | None = None
        self._model_predict_thread: ModelPredictorThread | None = None
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_predict.clicked.connect(self._on_export_clicked)

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

    def create_predict_thread(self) -> Optional[ModelPredictorThread]:
        self._model_predict_thread = ModelPredictorThread(
            self._task_info.task_dir / "weights" / self.cmb_model_name.currentText())
        self._model_predict_thread.model_predict_end.connect(self._on_predict_end)

    def predict(self):
        self.create_predict_thread()
        self._model_predict_thread.start()

    def _on_export_clicked(self):
        self.predict()

    def _on_predict_end(self, results):
        pprint(results)
