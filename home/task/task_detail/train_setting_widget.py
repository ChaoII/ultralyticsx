import enum
from pathlib import Path

import yaml
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QWidget, QGridLayout, QFormLayout, QVBoxLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, ComboBox, themeColor, CompactSpinBox, CompactDoubleSpinBox, SwitchButton, \
    CheckBox, LineEdit, StrongBodyLabel, SubtitleLabel, PushButton, PrimaryPushButton, FluentIcon, StateToolTip, \
    InfoBar, InfoBarPosition
from sqlalchemy import and_

from common.collapsible_widget import CollapsibleWidgetItem, ToolBox
from common.custom_icon import CustomFluentIcon
from common.db_helper import db_session
from common.model_type_widget import ModelType
from dataset.types import DatasetStatus
from home.options import model_type_list_map
from home.types import TaskInfo, TaskStatus
from models.models import Dataset, Task


class BatchStatus(enum.Enum):
    AUTO = 0
    Custom = 1


class Devices(enum.Enum):
    CPU = "cpu"
    GPU = "gpu"
    MPS = "mps"


class GPUCheckBox(CheckBox):
    check_state_changed = Signal(Qt.CheckState, str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setText(text)
        self.checkStateChanged.connect(self._on_status_changed)

    @Slot(Qt.CheckState)
    def _on_status_changed(self, status):
        self.check_state_changed.emit(status, self.text())


class DeviceWidget(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.cmb_devices = ComboBox()
        self.cmb_devices.addItems(["CPU", "GPU", "MPS"])
        self.cmb_devices.setItemData(0, Devices.CPU)
        self.cmb_devices.setItemData(1, Devices.GPU)
        self.cmb_devices.setItemData(2, Devices.MPS)
        self.cmb_devices.setCurrentIndex(0)
        self.cmb_devices.setFixedWidth(300)

        self.cb0 = GPUCheckBox(text="0")
        self.cb0.setCheckState(Qt.CheckState.Checked)
        self.cb1 = GPUCheckBox(text="1")
        self.cb1.setCheckState(Qt.CheckState.Unchecked)
        self.cb2 = GPUCheckBox(text="2")
        self.cb2.setCheckState(Qt.CheckState.Unchecked)
        self.cb3 = GPUCheckBox(text="3")
        self.cb3.setCheckState(Qt.CheckState.Unchecked)
        self.cb4 = GPUCheckBox(text="4")
        self.cb4.setCheckState(Qt.CheckState.Unchecked)
        self.cb5 = GPUCheckBox(text="5")
        self.cb5.setCheckState(Qt.CheckState.Unchecked)
        self.cb6 = GPUCheckBox(text="6")
        self.cb6.setCheckState(Qt.CheckState.Unchecked)
        self.cb7 = GPUCheckBox(text="7")
        self.cb7.setCheckState(Qt.CheckState.Unchecked)
        self._cb_device_map: dict[int, GPUCheckBox] = {
            0: self.cb0,
            1: self.cb1,
            2: self.cb2,
            3: self.cb3,
            4: self.cb4,
            5: self.cb5,
            6: self.cb6,
            7: self.cb7,
        }

        self.check_box_group = QWidget()
        self.hly_check_box = QHBoxLayout(self.check_box_group)
        self.hly_check_box.setSpacing(2)
        self.hly_check_box.setContentsMargins(0, 0, 0, 0)
        self.hly_check_box.addWidget(self.cb0)
        self.hly_check_box.addWidget(self.cb1)
        self.hly_check_box.addWidget(self.cb2)
        self.hly_check_box.addWidget(self.cb3)
        self.hly_check_box.addWidget(self.cb4)
        self.hly_check_box.addWidget(self.cb5)
        self.hly_check_box.addWidget(self.cb6)
        self.hly_check_box.addWidget(self.cb7)
        self.hly_check_box.addStretch(1)

        self.hly_content = QHBoxLayout(self)
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.hly_content.addWidget(self.cmb_devices)
        self.hly_content.addWidget(self.check_box_group)
        self.hly_content.addStretch(1)
        self.check_box_group.setHidden(True)

        self.cmb_devices.currentTextChanged.connect(self._on_device_changed)
        self.cb0.check_state_changed.connect(self._gpu_changed)
        self.cb1.check_state_changed.connect(self._gpu_changed)
        self.cb2.check_state_changed.connect(self._gpu_changed)
        self.cb3.check_state_changed.connect(self._gpu_changed)
        self.cb4.check_state_changed.connect(self._gpu_changed)
        self.cb5.check_state_changed.connect(self._gpu_changed)
        self.cb6.check_state_changed.connect(self._gpu_changed)
        self.cb7.check_state_changed.connect(self._gpu_changed)

        self._gpus: list[int] = [0]
        self._current_device = Devices.CPU

    def get_current_device(self):
        return [self._current_device, self._gpus]

    def set_value(self, value):
        if isinstance(value, str):
            self.cmb_devices.setText(value.upper())
            self.check_box_group.setHidden(True)
        elif isinstance(value, int | list):
            self.check_box_group.setHidden(False)
            if isinstance(value, int):
                value = [value]
            self.cmb_devices.setText("GPU")
            for i in range(8):
                if i in value:
                    self._cb_device_map[i].setChecked(True)
                else:
                    self._cb_device_map[i].setChecked(False)
        else:
            raise ValueError(f"expect 'cpu','mps',0,[0,1,2...],but get value{value}")

    @Slot(Qt.CheckState, str)
    def _gpu_changed(self, status: Qt.CheckState, text: str):
        gpu_index = int(text)
        if status == Qt.CheckState.Checked:
            if gpu_index not in self._gpus:
                self._gpus.append(gpu_index)
        if status == Qt.CheckState.Unchecked:
            if gpu_index in self._gpus:
                self._gpus.remove(gpu_index)

    @Slot(str)
    def _on_device_changed(self, text: str):
        self._current_device = self.cmb_devices.currentData()
        if self._current_device == Devices.GPU:
            self.check_box_group.setHidden(False)
        else:
            self.check_box_group.setHidden(True)


class BatchWidget(QWidget):
    batch_changed = Signal(bool, int)

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.hly_content = QHBoxLayout(self)
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.btn_batch = SwitchButton()
        self.btn_batch.setOffText(self.tr("Custom"))
        self.btn_batch.setOnText(self.tr("Auto"))
        self.btn_batch.setChecked(True)

        self.spb_batch = CompactSpinBox()
        self.spb_batch.setFixedWidth(180)
        self.spb_batch.setHidden(True)

        self.hly_content.addWidget(self.btn_batch)
        self.hly_content.addWidget(self.spb_batch)
        self.hly_content.addStretch(1)

        self.btn_batch.checkedChanged.connect(self._on_batch_status_changed)
        self.spb_batch.valueChanged.connect(self._on_batch_value_changed)
        self._is_auto_batch = True
        self._batch_size = -1

    def set_status(self, status: BatchStatus):
        if status == BatchStatus.AUTO:
            self.btn_batch.setChecked(True)
            self._is_auto_batch = True
        if status == BatchStatus.Custom:
            self.btn_batch.setChecked(False)
            self._is_auto_batch = False

    def value(self):
        return self._batch_size

    def set_value(self, value: int):
        if value == -1:
            self.btn_batch.setChecked(True)
            self.spb_batch.setHidden(True)
        else:
            self.btn_batch.setChecked(False)
            self.spb_batch.setValue(value)
            self.spb_batch.setHidden(False)

    @Slot(bool)
    def _on_batch_status_changed(self, is_auto_batch: bool):
        # 自动batch
        if is_auto_batch:
            self._batch_size = -1
            self.spb_batch.setHidden(True)
        else:
            self.spb_batch.setHidden(False)

    @Slot(int)
    def _on_batch_value_changed(self, value: int):
        self._batch_size = value


class FixWidthBodyLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(100)
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)


class TrainParameterWidget(CollapsibleWidgetItem):
    parameter_config_finished = Signal(TaskInfo)
    start_training_clicked = Signal(TaskInfo)

    def __init__(self, parent=None):
        super().__init__(self.tr("▌Parameter configuration"), parent=parent)
        # ------------------------训练参数-------------------------
        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setFixedWidth(300)

        self.cus_device = DeviceWidget()

        self.btn_pre_trained = SwitchButton()
        self.btn_pre_trained.setOffText(self.tr("Close"))
        self.btn_pre_trained.setOnText("Open")
        self.btn_pre_trained.setFixedWidth(200)
        self.btn_pre_trained.setFixedHeight(33)
        self.btn_pre_trained.setChecked(True)

        self.spb_epochs = CompactSpinBox()
        self.spb_epochs.setRange(0, 10000)
        self.spb_epochs.setValue(100)
        self.spb_epochs.setFixedWidth(300)

        self.spb_time = CompactDoubleSpinBox()
        self.spb_time.setFixedWidth(300)

        self.spb_patience = CompactSpinBox()
        self.spb_patience.setRange(0, 1000)
        self.spb_patience.setValue(100)
        self.spb_patience.setFixedWidth(300)

        self.cus_batch = BatchWidget()
        self.cus_batch.set_status(BatchStatus.AUTO)
        self.cus_batch.setFixedHeight(33)

        self.spb_image_size = CompactSpinBox()
        self.spb_image_size.setRange(32, 4860)
        self.spb_image_size.setValue(640)
        self.spb_image_size.setFixedWidth(300)

        self.spb_workers = CompactSpinBox()
        self.spb_workers.setRange(0, 8)
        self.spb_workers.setValue(0)
        self.spb_workers.setFixedWidth(300)

        self.cmb_optimizer = ComboBox()
        self.cmb_optimizer.addItems(["auto", "SGD", "Adam", "Adamax", "AdamW", "NAdam", "RAdam", "RMSProp"])
        self.cmb_optimizer.setCurrentIndex(0)
        self.cmb_optimizer.setFixedWidth(300)

        self.btn_verbose = SwitchButton()
        self.btn_verbose.setChecked(True)
        self.btn_verbose.setFixedHeight(33)

        self.spb_seed = CompactSpinBox()
        self.spb_seed.setValue(0)
        self.spb_seed.setFixedWidth(300)

        self.btn_rect = SwitchButton()
        self.btn_rect.setChecked(False)
        self.btn_rect.setFixedHeight(33)

        self.btn_cos_lr = SwitchButton()
        self.btn_cos_lr.setChecked(False)
        self.btn_cos_lr.setFixedHeight(33)

        self.spb_close_mosaic = CompactSpinBox()
        self.spb_close_mosaic.setValue(10)
        self.spb_close_mosaic.setFixedWidth(300)

        self.btn_resume = SwitchButton()
        self.btn_resume.setChecked(False)
        self.btn_resume.setFixedHeight(33)

        self.btn_amp = SwitchButton()
        self.btn_amp.setChecked(True)
        self.btn_resume.setFixedHeight(33)

        self.spb_fraction = CompactDoubleSpinBox()
        self.spb_fraction.setValue(1.0)
        self.spb_fraction.setFixedWidth(300)

        self.btn_profile = SwitchButton()
        self.btn_profile.setChecked(False)
        self.btn_profile.setFixedHeight(33)

        self.le_freeze = LineEdit()
        self.le_freeze.setFixedWidth(300)

        self.btn_multi_scale = SwitchButton()
        self.btn_multi_scale.setChecked(False)
        self.btn_multi_scale.setFixedHeight(33)

        self.btn_overlap_mask = SwitchButton()
        self.btn_overlap_mask.setChecked(True)
        self.btn_overlap_mask.setFixedHeight(33)

        self.spb_mask_ratio = CompactSpinBox()
        self.spb_mask_ratio.setValue(4)
        self.spb_mask_ratio.setFixedWidth(300)

        self.spb_dropout = CompactDoubleSpinBox()
        self.spb_dropout.setValue(0.0)
        self.spb_dropout.setFixedWidth(300)

        self.fly_train_setting1 = QFormLayout()
        self.fly_train_setting1.setVerticalSpacing(15)
        self.fly_train_setting1.setHorizontalSpacing(40)
        self.fly_train_setting1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_train_setting2 = QFormLayout()
        self.fly_train_setting2.setVerticalSpacing(15)
        self.fly_train_setting2.setHorizontalSpacing(40)
        self.fly_train_setting2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("Pre-trained: "), self), self.btn_pre_trained)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("epochs: "), self, ), self.spb_epochs)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("time: "), self, ), self.spb_time)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("patience: "), self, ), self.spb_patience)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("batch: "), self, ), self.cus_batch)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("image_size: "), self, ), self.spb_image_size)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("workers: "), self, ), self.spb_workers)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("optimizer: "), self, ), self.cmb_optimizer)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("verbose: "), self, ), self.btn_verbose)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("seed: "), self, ), self.spb_seed)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("rect: "), self, ), self.btn_rect)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("cos_lr: "), self, ), self.btn_cos_lr)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("close_mosaic: "), self, ), self.spb_close_mosaic)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("resume: "), self, ), self.btn_resume)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("amp: "), self, ), self.btn_amp)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("fraction: "), self, ), self.spb_fraction)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("profile: "), self, ), self.btn_profile)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("freeze: "), self, ), self.le_freeze)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("multi_scale: "), self, ), self.btn_multi_scale)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("overlap_mask: "), self, ), self.btn_overlap_mask)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("mask_ratio: "), self, ), self.spb_mask_ratio)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("dropout: "), self), self.spb_dropout)

        self.fly_model_name = QFormLayout()
        self.fly_model_name.setHorizontalSpacing(40)
        self.fly_model_name.addRow(FixWidthBodyLabel(self.tr("model name: "), self), self.cmb_model_name)

        self.fly_device = QFormLayout()
        self.fly_device.setHorizontalSpacing(40)
        self.fly_device.addRow(FixWidthBodyLabel(self.tr("device: "), self), self.cus_device)

        self.vly_train_setting = QVBoxLayout()
        self.vly_train_setting.setSpacing(15)
        self.vly_train_setting.setContentsMargins(20, 0, 20, 0)

        self.hly_train_setting = QHBoxLayout()
        self.hly_train_setting.setSpacing(40)
        self.hly_train_setting.addLayout(self.fly_train_setting1)
        self.hly_train_setting.addLayout(self.fly_train_setting2)
        self.hly_train_setting.addStretch(1)

        self.vly_train_setting.addLayout(self.fly_model_name)
        self.vly_train_setting.addLayout(self.fly_device)
        self.vly_train_setting.addLayout(self.hly_train_setting)

        # ---------------------超参数部分-----------------------------
        self.spb_lr0 = CompactDoubleSpinBox()
        self.spb_lr0.setValue(0.001)
        self.spb_lr0.setFixedWidth(300)

        self.spb_lrf = CompactDoubleSpinBox()
        self.spb_lrf.setValue(0.001)
        self.spb_lrf.setFixedWidth(300)

        self.spb_momentum = CompactDoubleSpinBox()
        self.spb_momentum.setValue(0.937)
        self.spb_momentum.setFixedWidth(300)

        self.spb_weight_decay = CompactDoubleSpinBox()
        self.spb_weight_decay.setValue(0.0005)
        self.spb_weight_decay.setFixedWidth(300)

        self.spb_warmup_epochs = CompactSpinBox()
        self.spb_warmup_epochs.setValue(3)
        self.spb_warmup_epochs.setFixedWidth(300)

        self.spb_warmup_momentum = CompactDoubleSpinBox()
        self.spb_warmup_momentum.setValue(0.8)
        self.spb_warmup_momentum.setFixedWidth(300)

        self.spb_warmup_bias_lr = CompactDoubleSpinBox()
        self.spb_warmup_bias_lr.setValue(0.1)
        self.spb_warmup_bias_lr.setFixedWidth(300)

        self.spb_box = CompactDoubleSpinBox()
        self.spb_box.setValue(7.5)
        self.spb_box.setFixedWidth(300)

        self.spb_cls = CompactDoubleSpinBox()
        self.spb_cls.setValue(0.5)
        self.spb_cls.setFixedWidth(300)

        self.spb_dfl = CompactDoubleSpinBox()
        self.spb_dfl.setValue(1.5)
        self.spb_dfl.setFixedWidth(300)

        self.spb_pose = CompactDoubleSpinBox()
        self.spb_pose.setValue(12.0)
        self.spb_pose.setFixedWidth(300)

        self.spb_kobj = CompactDoubleSpinBox()
        self.spb_kobj.setValue(1.0)
        self.spb_kobj.setFixedWidth(300)

        self.spb_label_smoothing = CompactDoubleSpinBox()
        self.spb_label_smoothing.setValue(0.0)
        self.spb_label_smoothing.setFixedWidth(300)

        self.spb_nbs = CompactSpinBox()
        self.spb_nbs.setValue(64)
        self.spb_nbs.setFixedWidth(300)

        self.fly_hyperparameters1 = QFormLayout()
        self.fly_hyperparameters1.setVerticalSpacing(15)
        self.fly_hyperparameters1.setHorizontalSpacing(40)
        self.fly_hyperparameters1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_hyperparameters2 = QFormLayout()
        self.fly_hyperparameters2.setVerticalSpacing(15)
        self.fly_hyperparameters2.setHorizontalSpacing(40)
        self.fly_hyperparameters2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("lr0: "), self), self.spb_lr0)
        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("lrf: "), self), self.spb_lrf)
        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("momentum: "), self), self.spb_momentum)
        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("weight_decay: "), self), self.spb_weight_decay)
        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("warmup_epochs: "), self), self.spb_warmup_epochs)
        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("warmup_momentum: "), self),
                                         self.spb_warmup_momentum)
        self.fly_hyperparameters1.addRow(FixWidthBodyLabel(self.tr("warmup_lr: "), self), self.spb_warmup_bias_lr)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("box: "), self), self.spb_box)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("cls: "), self), self.spb_cls)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("dfl: "), self), self.spb_dfl)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("pose: "), self), self.spb_pose)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("kobj: "), self), self.spb_kobj)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("label_smoothing: "), self),
                                         self.spb_label_smoothing)
        self.fly_hyperparameters2.addRow(FixWidthBodyLabel(self.tr("nbs: "), self), self.spb_nbs)

        self.hly_hyperparameters = QHBoxLayout()
        self.hly_hyperparameters.setContentsMargins(20, 0, 20, 0)
        self.hly_hyperparameters.setSpacing(40)
        self.hly_hyperparameters.addLayout(self.fly_hyperparameters1)
        self.hly_hyperparameters.addLayout(self.fly_hyperparameters2)
        self.hly_hyperparameters.addStretch(1)

        # ----------------data augment------------------------------
        self.spb_hsv_h = CompactDoubleSpinBox()
        self.spb_hsv_h.setValue(0.015)
        self.spb_hsv_h.setFixedWidth(300)

        self.spb_hsv_s = CompactDoubleSpinBox()
        self.spb_hsv_s.setValue(0.7)
        self.spb_hsv_s.setFixedWidth(300)

        self.spb_hsv_v = CompactDoubleSpinBox()
        self.spb_hsv_v.setValue(0.4)
        self.spb_hsv_v.setFixedWidth(300)

        self.spb_degrees = CompactDoubleSpinBox()
        self.spb_degrees.setValue(0.0)
        self.spb_degrees.setFixedWidth(300)

        self.spb_translate = CompactDoubleSpinBox()
        self.spb_translate.setValue(0.1)
        self.spb_translate.setFixedWidth(300)

        self.spb_scale = CompactDoubleSpinBox()
        self.spb_scale.setValue(0.5)
        self.spb_scale.setFixedWidth(300)

        self.spb_shear = CompactDoubleSpinBox()
        self.spb_shear.setValue(0.0)
        self.spb_shear.setFixedWidth(300)

        self.spb_perspective = CompactDoubleSpinBox()
        self.spb_perspective.setValue(0.0)
        self.spb_perspective.setFixedWidth(300)

        self.spb_flipud = CompactDoubleSpinBox()
        self.spb_flipud.setValue(0.0)
        self.spb_flipud.setFixedWidth(300)

        self.spb_fliplr = CompactDoubleSpinBox()
        self.spb_fliplr.setValue(0.5)
        self.spb_fliplr.setFixedWidth(300)

        self.spb_bgr = CompactDoubleSpinBox()
        self.spb_bgr.setValue(0.0)
        self.spb_bgr.setFixedWidth(300)

        self.spb_mosaic = CompactDoubleSpinBox()
        self.spb_mosaic.setValue(1.0)
        self.spb_mosaic.setFixedWidth(300)

        self.spb_mixup = CompactDoubleSpinBox()
        self.spb_mixup.setValue(0.0)
        self.spb_mixup.setFixedWidth(300)

        self.spb_copy_paste = CompactDoubleSpinBox()
        self.spb_copy_paste.setValue(0.0)
        self.spb_copy_paste.setFixedWidth(300)

        self.cmb_auto_augment = ComboBox()
        self.cmb_auto_augment.addItems(["randaugment", "autoaugment", "augmix"])
        self.cmb_auto_augment.setCurrentIndex(0)
        self.cmb_auto_augment.setFixedWidth(300)

        self.spb_erasing = CompactDoubleSpinBox()
        self.spb_erasing.setValue(0.4)
        self.spb_erasing.setFixedWidth(300)

        self.spb_crop_fraction = CompactDoubleSpinBox()
        self.spb_crop_fraction.setValue(1.0)
        self.spb_crop_fraction.setFixedWidth(300)

        self.fly_data_augment1 = QFormLayout()
        self.fly_data_augment1.setVerticalSpacing(15)
        self.fly_data_augment1.setHorizontalSpacing(40)
        self.fly_data_augment1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_data_augment2 = QFormLayout()
        self.fly_data_augment2.setVerticalSpacing(15)
        self.fly_data_augment2.setHorizontalSpacing(40)
        self.fly_data_augment2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("hsv_h: "), self), self.spb_hsv_h)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("hsv_s: "), self), self.spb_hsv_s)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("hsv_v: "), self), self.spb_hsv_v)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("degrees: "), self), self.spb_degrees)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("translate: "), self), self.spb_translate)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("scale: "), self), self.spb_scale)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("shear: "), self), self.spb_shear)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("perspective: "), self), self.spb_perspective)
        self.fly_data_augment1.addRow(FixWidthBodyLabel(self.tr("flipud: "), self), self.spb_flipud)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("fliplr: "), self), self.spb_fliplr)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("bgr: "), self), self.spb_bgr)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("mosaic: "), self), self.spb_mosaic)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("mixup: "), self), self.spb_mixup)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("copy_paste: "), self), self.spb_copy_paste)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("auto_augment: "), self), self.cmb_auto_augment)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("erasing: "), self), self.spb_erasing)
        self.fly_data_augment2.addRow(FixWidthBodyLabel(self.tr("crop_fraction: "), self), self.spb_crop_fraction)

        self.hly_data_augment = QHBoxLayout()
        self.hly_data_augment.setContentsMargins(20, 0, 20, 0)
        self.hly_data_augment.setSpacing(40)
        self.hly_data_augment.addLayout(self.fly_data_augment1)
        self.hly_data_augment.addLayout(self.fly_data_augment2)
        self.hly_data_augment.addStretch(1)

        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)

        self.vly_content = QVBoxLayout(self.content_widget)
        self.vly_content.setContentsMargins(20, 0, 20, 0)
        self.vly_content.setSpacing(30)
        self.title_train_settings = StrongBodyLabel(self.tr("▶ Train settings"), self)
        self.title_train_settings.setTextColor(themeColor(), themeColor())
        self.vly_content.addWidget(self.title_train_settings)
        self.vly_content.addLayout(self.vly_train_setting)
        self.title_Hyperparameters = StrongBodyLabel(self.tr("▶ Hyperparameters"), self)
        self.title_Hyperparameters.setTextColor(themeColor(), themeColor())
        self.vly_content.addWidget(self.title_Hyperparameters)
        self.vly_content.addLayout(self.hly_hyperparameters)
        self.title_data_augment = StrongBodyLabel(self.tr("▶ Data augment"), self)
        self.title_data_augment.setTextColor(themeColor(), themeColor())
        self.vly_content.addWidget(self.title_data_augment)
        self.vly_content.addLayout(self.hly_data_augment)

        self.btn_start_train = PrimaryPushButton(FluentIcon.PLAY, self.tr("Start training"))
        self.btn_start_train.setFixedWidth(150)
        self.btn_save = PushButton(FluentIcon.SAVE, self.tr("Save"))
        self.btn_save.setFixedWidth(150)
        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_start_train)
        self.hly_btn.addWidget(self.btn_save)
        self.hly_btn.addStretch(1)

        self.vly_content.addLayout(self.hly_btn)

        self.set_content_widget(self.content_widget)
        self._task_info: TaskInfo | None = None
        self.stateTooltip = None
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_start_train.clicked.connect(self._on_train_clicked)
        self.btn_save.clicked.connect(self._on_save_clicked)

    def _save_config(self):
        freeze = None
        if self.le_freeze.text():
            freeze = self.le_freeze.text()

        if self.cus_device.get_current_device()[0] != Devices.GPU:
            device = self.cus_device.get_current_device()[0].value
        else:
            device = self.cus_device.get_current_device()[1]

        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            data = (Path(task.dataset.dataset_dir) / "split").resolve().as_posix()

        parameter = dict(
            model=self.cmb_model_name.currentText(),
            data=data,
            epochs=self.spb_epochs.value(),
            time=self.spb_time.value(),
            patience=self.spb_patience.value(),
            batch=self.cus_batch.value(),
            imgsz=self.spb_image_size.value(),
            device=device,
            workers=self.spb_workers.value(),
            pretrained=self.btn_pre_trained.isChecked(),
            optimizer=self.cmb_optimizer.currentText(),
            verbose=self.btn_verbose.isChecked(),
            seed=self.spb_seed.value(),
            rect=self.btn_rect.isChecked(),
            cos_lr=self.btn_cos_lr.isChecked(),
            close_mosaic=self.spb_close_mosaic.value(),
            resume=self.btn_resume.isChecked(),
            amp=self.btn_amp.isChecked(),
            fraction=self.spb_fraction.value(),
            profile=self.btn_profile.isChecked(),
            freeze=freeze,
            multi_scale=self.btn_multi_scale.isChecked(),
            overlap_mask=self.btn_overlap_mask.isChecked(),
            mask_ratio=self.spb_mask_ratio.value(),
            dropout=self.spb_dropout.value(),

            lr0=self.spb_lr0.value(),
            lrf=self.spb_lrf.value(),
            momentum=self.spb_momentum.value(),
            weight_decay=self.spb_weight_decay.value(),
            warmup_epochs=self.spb_warmup_epochs.value(),
            warmup_momentum=self.spb_warmup_momentum.value(),
            warmup_bias_lr=self.spb_warmup_bias_lr.value(),
            box=self.spb_box.value(),
            cls=self.spb_cls.value(),
            dfl=self.spb_dfl.value(),
            pose=self.spb_pose.value(),
            kobj=self.spb_kobj.value(),
            label_smoothing=self.spb_label_smoothing.value(),
            nbs=self.spb_nbs.value(),

            hsv_h=self.spb_hsv_h.value(),
            hsv_s=self.spb_hsv_s.value(),
            hsv_v=self.spb_hsv_v.value(),
            degrees=self.spb_degrees.value(),
            translate=self.spb_translate.value(),
            scale=self.spb_scale.value(),
            shear=self.spb_shear.value(),
            perspective=self.spb_perspective.value(),
            flipud=self.spb_flipud.value(),
            fliplr=self.spb_fliplr.value(),
            bgr=self.spb_bgr.value(),
            mosaic=self.spb_mosaic.value(),
            mixup=self.spb_mixup.value(),
            copy_paste=self.spb_copy_paste.value(),
            auto_augment=self.cmb_auto_augment.currentText(),
            erasing=self.spb_erasing.value(),
            crop_fraction=self.spb_crop_fraction.value()
        )
        with open(self._task_info.task_dir / "train_config.yaml", 'w', encoding="utf8") as file:
            yaml.dump(parameter, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = TaskStatus.CFG_FINISHED.value
        self._task_info.task_status = TaskStatus.CFG_FINISHED

    def _on_train_clicked(self):
        self._save_config()
        self.start_training_clicked.emit(self._task_info)

    def _on_save_clicked(self):
        self._save_config()
        self.parameter_config_finished.emit(self._task_info)
        InfoBar.success(
            title='',
            content=self.tr("Parameter saved successfully"),
            orient=Qt.Orientation.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.parent().parent()
        )

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
        self._init_parameter_on_widget()

    def _init_parameter_on_widget(self):
        self.cmb_model_name.clear()
        self.cmb_model_name.addItems(model_type_list_map[self._task_info.model_type])
        if self._task_info.task_status.value >= TaskStatus.CFG_FINISHED.value:
            with open(self._task_info.task_dir / "train_config.yaml", 'r', encoding="utf8") as file:
                parameter = yaml.safe_load(file)
            self.cmb_model_name.setCurrentText(parameter["model"]),

            self.spb_epochs.setValue(parameter["epochs"])
            self.spb_time.setValue(parameter["time"])
            self.spb_patience.setValue(parameter["patience"])
            self.cus_batch.set_value(parameter["batch"])
            self.spb_image_size.setValue(parameter["imgsz"])
            self.cus_device.set_value(parameter["device"])
            self.spb_workers.setValue(parameter["workers"])
            self.btn_pre_trained.setChecked(parameter["pretrained"])
            self.cmb_optimizer.setCurrentText(parameter["optimizer"])
            self.btn_verbose.setChecked(parameter["verbose"])
            self.spb_seed.setValue(parameter["seed"])
            self.btn_rect.setChecked(parameter["rect"])
            self.btn_cos_lr.setChecked(parameter["cos_lr"])
            self.spb_close_mosaic.setValue(parameter["close_mosaic"])
            self.btn_resume.setChecked(parameter["resume"])
            self.btn_amp.setChecked(parameter["amp"])
            self.spb_fraction.setValue(parameter["fraction"])
            self.btn_profile.setChecked(parameter["profile"])
            self.le_freeze.setText(parameter["freeze"])
            self.btn_multi_scale.setChecked(parameter["multi_scale"])
            self.btn_overlap_mask.setChecked(parameter["overlap_mask"])
            self.spb_mask_ratio.setValue(parameter["mask_ratio"])
            self.spb_dropout.setValue(parameter["dropout"])

            self.spb_lr0.setValue(parameter["lr0"])
            self.spb_lrf.setValue(parameter["lrf"])
            self.spb_momentum.setValue(parameter["momentum"])
            self.spb_weight_decay.setValue(parameter["weight_decay"])
            self.spb_warmup_epochs.setValue(parameter["warmup_epochs"])
            self.spb_warmup_momentum.setValue(parameter["warmup_momentum"])
            self.spb_warmup_bias_lr.setValue(parameter["warmup_bias_lr"])
            self.spb_box.setValue(parameter["box"])
            self.spb_cls.setValue(parameter["cls"])
            self.spb_dfl.setValue(parameter["dfl"])
            self.spb_pose.setValue(parameter["pose"])
            self.spb_kobj.setValue(parameter["kobj"])
            self.spb_label_smoothing.setValue(parameter["label_smoothing"])
            self.spb_nbs.setValue(parameter["nbs"])

            self.spb_hsv_h.setValue(parameter["hsv_h"])
            self.spb_hsv_s.setValue(parameter["hsv_s"])
            self.spb_hsv_v.setValue(parameter["hsv_v"])
            self.spb_degrees.setValue(parameter["degrees"])
            self.spb_translate.setValue(parameter["translate"])
            self.spb_scale.setValue(parameter["scale"])
            self.spb_shear.setValue(parameter["shear"])
            self.spb_perspective.setValue(parameter["perspective"])
            self.spb_flipud.setValue(parameter["flipud"])
            self.spb_fliplr.setValue(parameter["fliplr"])
            self.spb_bgr.setValue(parameter["bgr"])
            self.spb_mosaic.setValue(parameter["mosaic"])
            self.spb_mixup.setValue(parameter["mixup"])
            self.spb_copy_paste.setValue(parameter["copy_paste"])
            self.cmb_auto_augment.setCurrentText(parameter["auto_augment"])
            self.spb_erasing.setValue(parameter["erasing"])
            self.spb_crop_fraction.setValue(parameter["crop_fraction"])
