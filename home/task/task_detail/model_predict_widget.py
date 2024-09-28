from pathlib import Path
from pprint import pprint
from typing import Optional

from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QAbstractItemView, QTableWidgetItem, \
    QSizePolicy
from qfluentwidgets import BodyLabel, ComboBox, CompactSpinBox, SwitchButton, \
    PrimaryPushButton, StateToolTip, \
    InfoBar, InfoBarPosition, ToolTipFilter, ToolTipPosition, ImageLabel, TableWidget, TextEdit

from common.model_type_widget import ModelType
from ultralytics.engine.results import Results

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_icon import CustomFluentIcon
from common.file_select_widget import FileSelectWidget
from common.image_select_widget import ImageSelectWidget
from common.image_show_widget import ImageShowWidget
from core.window_manager import WindowManager
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
        self.lbl_output_image = ImageShowWidget()
        self.lbl_output_image.setFixedSize(300, 400)

        self.lbl_output_result = TextEdit()
        self.lbl_output_result.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_output_result.setFixedWidth(300)
        self.lbl_output_result.setVisible(False)

        self.hly_tb_predict_speed = QHBoxLayout()
        self.tb_predict_speed = TableWidget()
        self.tb_predict_speed.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tb_predict_speed.setVisible(False)
        self.tb_predict_speed.verticalHeader().hide()
        self.tb_predict_speed.setBorderRadius(8)
        self.tb_predict_speed.setBorderVisible(True)
        self.hly_tb_predict_speed.addWidget(self.tb_predict_speed)
        self.hly_tb_predict_speed.addStretch(1)

        self.vly_result = QVBoxLayout()
        self.vly_result.addWidget(self.lbl_output_result)
        self.vly_result.addLayout(self.hly_tb_predict_speed)

        self.hly_images = QHBoxLayout()
        self.hly_images.addWidget(self.lbl_input_image)
        self.hly_images.addWidget(self.lbl_output_image)
        self.hly_images.addLayout(self.vly_result)
        self.hly_images.addStretch(1)

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
        self._current_image_path: Path | None = None
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_predict.clicked.connect(self._on_predict_clicked)
        self.lbl_input_image.image_selected.connect(self._on_image_selected)

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

    def create_predict_thread(self):
        self._model_predict_thread = ModelPredictorThread(
            self._task_info.task_dir / "weights" / self.cmb_model_name.currentText())
        self._model_predict_thread.model_predict_end.connect(self._on_predict_end)

    def predict(self):
        self.create_predict_thread()
        if not self._current_image_path:
            InfoBar.error(
                title="",
                content=self.tr("Please select a image"),
                duration=-1,
                position=InfoBarPosition.TOP_RIGHT,
                parent=WindowManager().find_window("main_widget")
            )
            return
        self._model_predict_thread.set_predict_image(self._current_image_path)
        self._model_predict_thread.start()

    def _on_image_selected(self, image_path: str):
        self._current_image_path = Path(image_path)

    def _on_predict_clicked(self):
        self.predict()

    def _on_predict_end(self, results: list[Results]):
        result = results[0]

        pprint(result)
        pprint(result.probs)
        self.lbl_output_result.setVisible(True)
        self.lbl_output_result.append("top1:")
        self.lbl_output_result.append(f"  -{result.names[result.probs.top1]:<30}: {float(result.probs.top1conf):.2f}")
        self.lbl_output_result.append("top5:")
        top5_text = ""
        for index, data in enumerate(result.probs.top5):
            top5_text += f"  -{result.names[data]:<30}: {float(result.probs.top5conf[index]):.2f}\n"
        self.lbl_output_result.append(top5_text)

        self.tb_predict_speed.setVisible(True)
        predict_speed = result.speed

        self.tb_predict_speed.setRowCount(1)
        self.tb_predict_speed.setColumnCount(len(predict_speed.keys()))
        self.tb_predict_speed.setHorizontalHeaderLabels(list(predict_speed.keys()))

        for col, speed in enumerate(predict_speed.values()):
            item = QTableWidgetItem(f"{speed:.4f}")
            self.tb_predict_speed.setItem(0, col, item)
        self.tb_predict_speed.resizeColumnsToContents()
        min_height = self.tb_predict_speed.horizontalHeader().height()
        min_width = 0
        for row in range(self.tb_predict_speed.rowCount()):
            min_height += self.tb_predict_speed.rowHeight(row)

        for col in range(self.tb_predict_speed.columnCount()):
            min_width += self.tb_predict_speed.columnWidth(col)
        self.tb_predict_speed.setFixedSize(min_width + 5, min_height + 5)
