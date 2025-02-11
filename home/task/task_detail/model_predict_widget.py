from pathlib import Path

import yaml
from PySide6.QtGui import Qt, QFont, QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QAbstractItemView, QTableWidgetItem, \
    QSizePolicy, QFormLayout
from qfluentwidgets import BodyLabel, ComboBox, PrimaryPushButton, InfoBar, InfoBarPosition, ToolTipFilter, \
    ToolTipPosition, TableWidget, TextEdit, CompactSpinBox

from common.component.collapsible_widget import CollapsibleWidgetItem
from common.component.custom_icon import CustomFluentIcon
from common.component.image_select_widget import ImageSelectWidget
from common.component.image_show_widget import ImageShowWidget
from common.component.model_type_widget import ModelType
from common.component.progress_message_box import ProgressMessageBox
from common.core.window_manager import window_manager
from common.utils.draw_labels import draw_image
from ultralytics.engine.results import Results
from ..task_thread.model_predict_thread import ModelPredictorThread
from ...types import TrainTaskInfo


class FixWidthBodyLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(100)
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))


class ModelPredictWidget(CollapsibleWidgetItem):

    def __init__(self, parent=None):
        super().__init__(self.tr("▌Model prediction"), parent=parent)
        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setFixedWidth(300)
        self.spb_image_size = CompactSpinBox()
        self.spb_image_size.setRange(64, 2560)
        self.spb_image_size.setValue(640)
        self.spb_image_size.setFixedWidth(300)
        self.btn_predict = PrimaryPushButton(CustomFluentIcon.MODEL_EXPORT, self.tr("Predict"))
        self.btn_predict.setFixedWidth(120)
        self.fly_model_name = QFormLayout()
        self.fly_model_name.addRow(self.tr("Model name:"), self.cmb_model_name)
        self.fly_image_size = QFormLayout()
        self.fly_image_size.addRow(self.tr("Image size:"), self.spb_image_size)
        self.hly_export_setting = QHBoxLayout()
        self.hly_export_setting.addLayout(self.fly_model_name)
        self.hly_export_setting.addLayout(self.fly_image_size)
        self.hly_export_setting.addWidget(self.btn_predict)

        self.hly_export_setting.addStretch(1)
        self._lbl_image_fix_width = 360
        self._lbl_image_fix_height = 300
        self.lbl_input_image = ImageSelectWidget()
        self.lbl_input_image.setFixedSize(self._lbl_image_fix_width, self._lbl_image_fix_height)
        self.lbl_input_image.set_border_radius(10, 10, 10, 10)
        self.lbl_output_image = ImageShowWidget()
        self.lbl_output_image.setFixedSize(self._lbl_image_fix_width, self._lbl_image_fix_height)

        self.lbl_output_result = TextEdit()
        self.lbl_output_result.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_output_result.setMinimumWidth(300)
        self.lbl_output_result.setVisible(False)

        font = QFont("Courier")  # "Courier" 是常见的等宽字体
        font.setWeight(QFont.Weight.Normal)
        font.setPixelSize(14)
        font.setStyleHint(QFont.StyleHint.Monospace)  # 设置字体风格提示为 Monospace (等宽字体)
        self.lbl_output_result.setFont(font)

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
        self.set_content_widget(self.content_widget)

        self._task_info: TrainTaskInfo | None = None
        self._model_predict_thread: ModelPredictorThread | None = None
        self._current_image_path: Path | None = None
        self._message_box: ProgressMessageBox | None = None
        self._connect_signals_and_slots()
        self._is_compact = False

    def _connect_signals_and_slots(self):
        self.btn_predict.clicked.connect(self._on_predict_clicked)
        self.lbl_input_image.image_selected.connect(self._on_image_selected)
        self.lbl_output_image.compact_mode_clicked.connect(self.on_compact_clicked)

    def on_compact_clicked(self, checked: bool):
        self._is_compact = checked
        self.draw_image_label()

    def set_task_info(self, task_info: TrainTaskInfo):
        self._task_info = task_info
        self._init_model_name()
        self._init_imgsz()
        self.tb_predict_speed.clear()
        self.tb_predict_speed.setVisible(False)
        self.lbl_output_result.clear()
        self.lbl_output_result.setVisible(False)
        self.lbl_input_image.clear()
        self.lbl_output_image.clear()

    def _init_imgsz(self):
        train_config_path = self._task_info.task_dir / "train_config.yaml"
        if train_config_path.exists():
            with open(train_config_path, mode="r", encoding="utf8") as f:
                train_config = yaml.safe_load(f)
                self.spb_image_size.setValue(train_config.get("imgsz", 640))

    def _init_model_name(self):
        self.cmb_model_name.clear()
        model_weight_path = self._task_info.task_dir / "weights"
        if not model_weight_path.exists():
            return
        for item in model_weight_path.iterdir():
            self.cmb_model_name.addItem(item.name)
        self.cmb_model_name.setCurrentIndex(0)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        width = int(event.size().width() / 3 - 8)
        height = int(width / self._lbl_image_fix_width * self._lbl_image_fix_height)
        self.lbl_input_image.setFixedSize(width, height)
        self.lbl_output_image.setFixedSize(width, height)

    def create_predict_thread(self):
        self._model_predict_thread = ModelPredictorThread(
            self._task_info.task_dir / "weights" / self.cmb_model_name.currentText())
        self._model_predict_thread.model_predict_end.connect(self._on_predict_end)
        self._model_predict_thread.model_predict_failed.connect(self._on_predict_failed)

    def _close_message_box(self, is_error: bool = False):
        if self._message_box:
            if is_error:
                self._message_box.set_error(True)
            self._message_box.close()

    def predict(self):
        self.create_predict_thread()
        if not self._current_image_path:
            InfoBar.error(
                title="",
                content=self.tr("Please select a image"),
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=window_manager.find_window("main_widget")
            )
            return
        kwargs = dict(
            imgsz=self.spb_image_size.value(),
        )
        self._model_predict_thread.set_predict_image(self._current_image_path)
        self._model_predict_thread.set_args(kwargs)
        self._model_predict_thread.start()
        self._message_box = ProgressMessageBox(indeterminate=True, parent=window_manager.find_window("main_widget"))
        self._message_box.set_ring_size(100, 100)
        self._message_box.exec()

    def _on_image_selected(self, image_path: str):
        self._current_image_path = Path(image_path)

    def _on_predict_clicked(self):
        self.predict()

    def _on_predict_failed(self, err_msg: str):
        self._close_message_box(is_error=True)
        InfoBar.error(
            title="",
            content=err_msg,
            duration=-1,
            position=InfoBarPosition.TOP_RIGHT,
            parent=window_manager.find_window("main_widget")
        )

    def draw_image_label(self):
        self.lbl_output_image.clear()
        image = draw_image(self._current_image_path.resolve().as_posix(),
                           self._task_info.model_type, self.result, self._is_compact)
        self.lbl_output_image.set_image(image)

    def _on_predict_end(self, result: Results):
        self._close_message_box()
        self.result = result
        self.draw_image_label()
        self.lbl_output_result.clear()
        self.lbl_output_result.setVisible(True)
        if self._task_info.model_type == ModelType.CLASSIFY:
            self.lbl_output_result.append("top1:")
            self.lbl_output_result.append(
                f"  -{result.names[result.probs.top1]:<15}: {float(result.probs.top1conf):.4f}")
            self.lbl_output_result.append("top5:")
            top5_text = ""
            for index, data in enumerate(result.probs.top5):
                top5_text += f"  -{result.names[data]:<15}: {float(result.probs.top5conf[index]):.2f}\n"
            self.lbl_output_result.append(top5_text)
        if self._task_info.model_type == ModelType.DETECT:
            txt = ""
            for index, box in enumerate(result.boxes.data.cpu().tolist()):
                txt += f"box{index}:\n"
                txt += f"  -{'class':<10}:{result.names[int(box[5])]}\n"
                txt += f"  -{'conf':<10}:{box[4]:.4f}\n"
                txt += f"  -{'x1':<10}:{box[0]:.4f}\n"
                txt += f"  -{'y1':<10}:{box[1]:.4f}\n"
                txt += f"  -{'x2':<10}:{box[2]:.4f}\n"
                txt += f"  -{'y2':<10}:{box[3]:.4f}\n"
            self.lbl_output_result.append(txt)
        if self._task_info.model_type == ModelType.SEGMENT:
            txt = ""
            for index, box in enumerate(result.boxes.data.cpu().tolist()):
                txt += f"box{index}:\n"
                txt += f"  -{'class':<10}:{result.names[int(box[5])]}\n"
                txt += f"  -{'conf':<10}:{box[4]:.4f}\n"
                txt += f"  -{'x1':<10}:{box[0]:.4f}\n"
                txt += f"  -{'y1':<10}:{box[1]:.4f}\n"
                txt += f"  -{'x2':<10}:{box[2]:.4f}\n"
                txt += f"  -{'y2':<10}:{box[3]:.4f}\n"
                txt += f"  -{'mask':<10}\n"
                txt += "    [\n"
                for x, y in result.masks.xy[index]:
                    txt += f"     [{x:.2f}, {y:.2f}]\n"
                txt += "    ]\n"
            self.lbl_output_result.append(txt)
        if self._task_info.model_type == ModelType.OBB:
            txt = ""
            for index, (cls, conf, box) in enumerate(zip(result.obb.cls.cpu().tolist(), result.obb.conf.cpu().tolist(),
                                                         result.obb.xyxyxyxy.cpu().tolist())):
                txt += f"box{index}:\n"
                txt += f"  -{'class':<10}:{result.names[int(cls)]}\n"
                txt += f"  -{'conf':<10}:{conf:.4f}\n"
                txt += f"  -{'x1':<10}:{box[0][0]:.4f}\n"
                txt += f"  -{'y1':<10}:{box[0][1]:.4f}\n"
                txt += f"  -{'x2':<10}:{box[1][0]:.4f}\n"
                txt += f"  -{'y2':<10}:{box[1][1]:.4f}\n"
                txt += f"  -{'x3':<10}:{box[2][0]:.4f}\n"
                txt += f"  -{'y3':<10}:{box[2][1]:.4f}\n"
                txt += f"  -{'x4':<10}:{box[3][0]:.4f}\n"
                txt += f"  -{'y4':<10}:{box[3][1]:.4f}\n"
            self.lbl_output_result.append(txt)
        if self._task_info.model_type == ModelType.POSE:
            txt = ""
            for index, box in enumerate(result.boxes.data.cpu().tolist()):
                txt += f"box{index}:\n"
                txt += f"  -{'class':<10}:{result.names[int(box[5])]}\n"
                txt += f"  -{'conf':<10}:{box[4]:.4f}\n"
                txt += f"  -{'x1':<10}:{box[0]:.4f}\n"
                txt += f"  -{'y1':<10}:{box[1]:.4f}\n"
                txt += f"  -{'x2':<10}:{box[2]:.4f}\n"
                txt += f"  -{'y2':<10}:{box[3]:.4f}\n"
                txt += f"  -{'key_points':<10}\n"
                txt += "    [\n"
                for x, y, c in result.keypoints.data.cpu().tolist()[index]:
                    txt += f"     [{x:.2f}, {y:.2f}, {c:.2f}]\n"
                txt += "    ]\n"
            self.lbl_output_result.append(txt)

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

        InfoBar.success(
            title="",
            content=self.tr("Predict successfully"),
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=window_manager.find_window("main_widget")
        )
