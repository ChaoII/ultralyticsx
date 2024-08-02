from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QPushButton, QGroupBox, QGridLayout,
                               QLineEdit, QTextEdit, QProgressBar, QComboBox, QCheckBox, QFileDialog, QFormLayout)
from .options import *
from PySide6.QtCore import Slot, Signal, Qt, QThread, QCoreApplication
from loguru import logger
import threading
from .trainer import ModelTrainThread, log_format_info, log_format_error, log_format_warning
from qfluentwidgets import HeaderCardWidget, BodyLabel, ComboBox, CheckBox, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressRing, ProgressBar, TextEdit
from pathlib import Path

from .model_info_card import ModelInfoCard
from .model_train_parameter_card import ModelTrainParamCard, TrainParameter


class CustomProcessBar(QWidget):
    def __init__(self, parent=None):
        super(CustomProcessBar, self).__init__(parent=parent)
        self.value = 0
        self.max_value = 0

        self.psb_hly = QHBoxLayout(self)
        self.psb_train = ProgressBar()
        self.lbl_train_process = BodyLabel(f"{self.value:>3} / {self.max_value:<3}", self)
        self.psb_hly.addWidget(self.psb_train)
        self.psb_hly.addWidget(self.lbl_train_process)

    def set_value(self, value):
        self.value = value
        self.psb_train.setValue(value)
        self.lbl_train_process.setText(f"{self.value:>3} / {self.max_value:<3}")

    def set_max_value(self, max_value):
        self.max_value = max_value
        self.psb_train.setMaximum(max_value)
        self.lbl_train_process.setText(f"{self.value:>3} / {self.max_value:<3}")


class ModelTrainWidget(QWidget):
    start_train_model_signal = Signal(str, int, int, float, int)
    stop_train_model_signal = Signal()

    def __init__(self, parent=None):
        super(ModelTrainWidget, self).__init__(parent=parent)
        self.setObjectName("model_train_widget")

        self.model_info_card = ModelInfoCard()
        self.model_train_param_card = ModelTrainParamCard()

        gly_btn = QGridLayout()
        # gly_btn.setContentsMargins(20, 10, 20, 10)
        self.btn_start_train = PrimaryPushButton(FluentIcon.PLAY, self.tr("start train"))
        self.btn_stop_train = PushButton(FluentIcon.PAUSE, self.tr("stop train"))

        self.psb_train = CustomProcessBar()
        self.psb_train.set_max_value(self.model_train_param_card.get_epochs())

        gly_btn.addWidget(self.btn_start_train, 0, 0)
        gly_btn.addWidget(self.btn_stop_train, 0, 1)
        gly_btn.addWidget(self.psb_train, 0, 2)

        self.psb_train.set_value(0)
        self.ted_train_log = TextEdit()

        vly_train_log = QVBoxLayout()
        vly_train_log.addWidget(self.ted_train_log)

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.model_info_card)
        v_layout.addWidget(self.model_train_param_card)
        v_layout.addLayout(gly_btn)
        v_layout.addLayout(vly_train_log)

        self.btn_stop_train.setEnabled(False)
        self._train_param = TrainParameter()
        self._connect_signals_and_slot()

    def _connect_signals_and_slot(self):
        self.model_train_param_card.train_param_changed.connect(self._on_train_param_changed)

    @Slot(TrainParameter)
    def _on_train_param_changed(self, train_param: TrainParameter):
        self._train_param = train_param
        self.psb_train.set_max_value(int(self._train_param.epoch))

# self.le_epoch.textChanged.connect(lambda x: self.psb_train.setMaximum(int(x)))

#     self.btn_start_train.clicked.connect(self.start_train)
#     self.btn_stop_train.clicked.connect(self.stop_train)
#     self.btn_select_data_config.clicked.connect(self.select_data_config)
#
#     # define
#     self.model_thread = None
#     self.current_model_name = ""
#     self.use_pretrain = False
#     self._train_finished = True
#     self._resume = False
#     self._last_model = ""
#     self._init_model_type_and_name_cmb()
#
# def _init_model_type_and_name_cmb(self):
#     # 初始化模型类型列表
#     for model_type in model_type_option:
#         pass
#         # self.cmb_model_type.addItem(model_type)
#     # 初始化模型名称
#     model_names = type_model_mapping.get(model_type_option[0], [])
#     for model_name in model_names:
#         pass
#         # self.cmb_model_name.addItem(model_name)
#     # 初始化模型
#     # self.current_model_name = self.cmb_model_name.currentText()
#
# def _initial_model(self,
#                    current_model_name: str,
#                    use_pretrain: bool,
#                    data_config: str,
#                    epochs: int,
#                    batch_size: int,
#                    learning_rate: float,
#                    workers: int,
#                    resume: bool):
#     logger.info(f"main thread, thread id is: {threading.get_ident()}")
#     self.model_thread = ModelTrainThread(current_model_name,
#                                          use_pretrain,
#                                          data_config,
#                                          epochs,
#                                          batch_size,
#                                          learning_rate,
#                                          workers,
#                                          resume)
#     self._train_finished = False
#     self.model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
#     self.model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
#     self.model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
#     self.model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
#     self.model_thread.train_end_signal.connect(self.on_handle_train_end)
#
#     self.stop_train_model_signal.connect(self.model_thread.stop_train)
#
# @Slot(str)
# def _set_model_name(self, model_type: str):
#     # self.cmb_model_name.clear()
#     model_names = type_model_mapping.get(model_type, [])
#     for model_name in model_names:
#         pass
#         # self.cmb_model_name.addItem(model_name)
#     pass
#
# def _turn_widget_enable_status(self):
#     # self.cmb_model_type.setEnabled(not self.cmb_model_type.isEnabled())
#     # self.cmb_model_name.setEnabled(not self.cmb_model_name.isEnabled())
#     self.ckb_use_pretrain.setEnabled(not self.ckb_use_pretrain.isEnabled())
#
#     self.le_epoch.setEnabled(not self.le_epoch.isEnabled())
#     self.le_batch.setEnabled(not self.le_batch.isEnabled())
#     self.le_learning_rate.setEnabled(not self.le_learning_rate.isEnabled())
#     self.le_workers.setEnabled(not self.le_workers.isEnabled())
#     self.le_train_data_config.setEnabled(not self.le_train_data_config.isEnabled())
#
#     self.btn_start_train.setEnabled(not self.btn_start_train.isEnabled())
#     self.btn_stop_train.setEnabled(not self.btn_stop_train.isEnabled())
#
# @Slot()
# def start_train(self):
#     self.ted_train_log.append(log_format_info(f"模型{self.current_model_name}开始训练"))
#     if not self._train_finished:
#         self._resume = True
#     if self._last_model:
#         current_model_name = self._last_model
#     else:
#         current_model_name = self.current_model_name
#         self._resume = False
#
#     self._initial_model(current_model_name, self.use_pretrain,
#                         self.le_train_data_config.text(),
#                         int(self.le_epoch.text()), int(self.le_batch.text()),
#                         float(self.le_learning_rate.text()),
#                         int(self.le_workers.text()), self._resume)
#     self._turn_widget_enable_status()
#     self.model_thread.start()
#
# @Slot(str)
# def on_model_name_changed(self, model_name: str):
#     self.current_model_name = model_name
#
# @Slot(Qt.CheckState)
# def on_use_pretrain_model_status_changed(self, status: Qt.CheckState):
#     self.use_pretrain = Qt.CheckState.Checked == status
#
# @Slot()
# def stop_train(self):
#     self.stop_train_model_signal.emit()
#     self.model_thread.quit()
#     self.model_thread.wait()
#     self._turn_widget_enable_status()
#     # 立即刷新界面
#     QCoreApplication.processEvents()
#     self.ted_train_log.append(log_format_info("用户手动停止，训练结束，点击开始训练可以继续执行训练"))
#
# @Slot(str)
# def on_handle_epoch_start(self, split: str):
#     self.ted_train_log.append(split)
#
# @Slot(str)
# def on_handle_batch_end(self, metrics: str):
#     self.ted_train_log.append(metrics)
#
# @Slot(int, str)
# def on_handle_epoch_end(self, epoch: int, last_model: str):
#     self._last_model = last_model
#     self.psb_train.setValue(epoch)
#
# @Slot(str)
# def on_handle_fit_epoch_end(self, format_metrics: str):
#     self.ted_train_log.append(format_metrics)
#
# @Slot(int)
# def on_handle_train_end(self, cur_epoch: int):
#     self._turn_widget_enable_status()
#     self._train_finished = True
#     if cur_epoch == int(self.le_epoch.text()):
#         self.ted_train_log.append(log_format_info(f"训练完成epoch = {cur_epoch}"))
#     else:
#         self.ted_train_log.append(log_format_info(f"训练提前完成，当前epoch = {cur_epoch}"))
#
# @Slot()
# def select_data_config(self):
#     file_name, _ = QFileDialog.getOpenFileName(self, "打开数据集配置文件", "", "All Files (*);;yaml (yaml,yml)")
#     self.le_train_data_config.setText(Path(file_name).resolve().as_posix())
