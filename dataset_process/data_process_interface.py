from pathlib import Path

from PySide6.QtCore import Slot, Qt, QSize, Signal
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QSizePolicy, QFileDialog, QFormLayout, QSplitter)
from qfluentwidgets import HeaderCardWidget, BodyLabel, LineEdit, PrimaryPushButton, FluentIcon, TextEdit, \
    StateToolTip

from utils.utils import *
from .data_convert_thread import DataConvertThread, LoadDatasetInfo
from .dataset_show_widget import DatasetDrawWidget

SMALL = QSize(60, 60)
MEDIUM = QSize(120, 120)
LARGE = QSize(200, 200)

RESOLUTIONS = [SMALL, MEDIUM, LARGE]
DATASET_TYPES = ["train", "val", "test"]


class SelectDatasetCard(HeaderCardWidget):
    """ Model information card """
    dataset_file_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("select dataset"))
        self.lbl_dataset = BodyLabel(self.tr('dataset file: '), self)
        self.led_dataset = LineEdit()
        self.led_dataset.setPlaceholderText(self.tr("please select a dataset file for zip"))
        self.btn_load_dataset = PrimaryPushButton(FluentIcon.UPDATE,
                                                  self.tr('select folder'))

        self.hly_dataset = QHBoxLayout(self)
        self.hly_dataset.addWidget(self.lbl_dataset)
        self.hly_dataset.addWidget(self.led_dataset)
        self.hly_dataset.addWidget(self.btn_load_dataset)

        self.viewLayout.addLayout(self.hly_dataset)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_load_dataset.clicked.connect(self.open_file)

    @Slot()
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, self.tr("open dataset file"), "",
                                                   "All Files (*);; Zip File(*.zip)")
        normalize_file_path = Path(file_name).resolve().as_posix()
        self.led_dataset.setText(normalize_file_path)
        self.dataset_file_changed.emit(normalize_file_path)


class DataProcessWidget(QWidget):
    def __init__(self, parent=None):
        super(DataProcessWidget, self).__init__(parent=parent)
        self.setObjectName("dataset_process")

        self.select_card = SelectDatasetCard(self)
        self.btn_data_valid = PrimaryPushButton(FluentIcon.UPDATE, self.tr('data valid'))

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.dataset_info_widget = QWidget()
        self.plot_dataset_info_widget = QWidget()

        fly_dataset_info = QFormLayout()
        fly_dataset_info.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_train_image_num = BodyLabel("training images: ", self)
        self.le_train_image_num = LineEdit()

        self.lbl_train_obj_num = BodyLabel("training object: ", self)
        self.le_train_obj_num = LineEdit()

        self.lbl_val_image_num = BodyLabel("valid images: ", self)
        self.le_val_image_num = LineEdit()

        self.lbl_val_obj_num = BodyLabel("valid object: ", self)
        self.le_val_obj_num = LineEdit()

        self.lbl_test_image_num = BodyLabel("test images: ", self)
        self.le_test_image_num = LineEdit()

        self.lbl_test_obj_num = BodyLabel("test objects: ", self)
        self.le_test_obj_num = LineEdit()

        self.lbl_dataset_config_path = BodyLabel("dataset config path: ", self)
        self.le_dataset_config_path = LineEdit()

        self.lbl_dataset_labels = BodyLabel("dataset labels: ", self)
        self.ted_dataset_labels = TextEdit()

        fly_dataset_info.addRow(self.lbl_train_image_num, self.le_train_image_num)
        fly_dataset_info.addRow(self.lbl_train_obj_num, self.le_train_obj_num)
        fly_dataset_info.addRow(self.lbl_val_image_num, self.le_val_image_num)
        fly_dataset_info.addRow(self.lbl_val_obj_num, self.le_val_obj_num)
        fly_dataset_info.addRow(self.lbl_test_image_num, self.le_test_image_num)
        fly_dataset_info.addRow(self.lbl_test_obj_num, self.le_test_obj_num)
        fly_dataset_info.addRow(self.lbl_dataset_config_path, self.le_dataset_config_path)
        fly_dataset_info.addRow(self.lbl_dataset_labels, self.ted_dataset_labels)

        self.dataset_info_widget.setLayout(fly_dataset_info)
        self.dataset_draw_widget = DatasetDrawWidget()
        self.splitter.addWidget(self.dataset_info_widget)
        self.splitter.addWidget(self.dataset_draw_widget)

        v_layout = QVBoxLayout(self)

        v_layout.addWidget(self.select_card)
        v_layout.addWidget(self.btn_data_valid)
        v_layout.addWidget(self.splitter)

        self.state_tool_tip = None

        self.data_convert_thread = DataConvertThread()
        self._connect_signals_and_slot()

    def _connect_signals_and_slot(self):
        self.btn_data_valid.clicked.connect(self.data_valid)
        self.select_card.dataset_file_changed.connect(self._on_update_dataset)
        self.data_convert_thread.dataset_resolve_finished.connect(self._on_dataset_resolve_finished)

    @Slot(str)
    def _on_update_dataset(self, dataset_path: str):
        self.data_convert_thread.set_dataset_path(dataset_path)

    @Slot(LoadDatasetInfo)
    def _on_dataset_resolve_finished(self, dataset_info: LoadDatasetInfo):
        self.le_train_image_num.setText(str(dataset_info.train_image_num))
        self.le_train_obj_num.setText(str(dataset_info.train_obj_num))
        self.le_val_image_num.setText(str(dataset_info.val_image_num))
        self.le_val_obj_num.setText(str(dataset_info.val_obj_num))
        self.le_test_image_num.setText(str(dataset_info.test_image_num))
        self.le_test_obj_num.setText(str(dataset_info.test_obj_num))
        self.le_dataset_config_path.setText(dataset_info.dst_yaml_path)
        self.ted_dataset_labels.append("\n".join(f"{k}: {v}" for k, v in dataset_info.labels.items()))

        self.dataset_draw_widget.draw_images(dataset_info)

        # 数据转换完成，显示状态信息
        self.state_tool_tip.setContent(
            self.tr('data converting is completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None

    @Slot()
    def data_valid(self):
        self.clear_cache()
        self.data_convert_thread.start()
        # 设置状态工具栏并显示
        self.state_tool_tip = StateToolTip(
            self.tr('data converting'), self.tr('please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()

    def clear_cache(self):
        self.dataset_draw_widget.lw_image.clear()
        self.le_train_image_num.clear()
        self.le_train_obj_num.clear()
        self.le_val_image_num.clear()
        self.le_val_obj_num.clear()
        self.le_test_image_num.clear()
        self.le_test_obj_num.clear()
        self.le_dataset_config_path.clear()
        self.ted_dataset_labels.clear()
