import json

import yaml
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSplitter)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, StateToolTip

from common.collapsible_widget import CollapsibleWidgetItem
from common.utils import log_info, log_warning, format_log
from model_train.train_parameter_widget import TrainParameter
from model_train.trainer import ModelTrainThread


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


class ModelTrainWidget(CollapsibleWidgetItem):
    start_train_model_signal = Signal(str, int, int, float, int)
    stop_train_model_signal = Signal()

    def __init__(self, parent=None):
        super(ModelTrainWidget, self).__init__(self.tr("▌Model training"), parent=parent)
        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)
        self.vly = QVBoxLayout(self.content_widget)
        self.vly.setContentsMargins(20, 0, 20, 0)
        self.set_content_widget(self.content_widget)

        self.btn_start_train = PrimaryPushButton(FluentIcon.PLAY, self.tr("start train"))
        self.btn_stop_train = PushButton(FluentIcon.PAUSE, self.tr("stop train"))
        self.psb_train = CustomProcessBar()
        self.psb_train.set_value(0)
        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_start_train)
        self.hly_btn.addWidget(self.btn_stop_train)
        self.hly_btn.addWidget(self.psb_train)

        self.ted_train_log = TextEdit()
        self.ted_train_log.setMinimumHeight(400)

        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.ted_train_log)

        self.btn_stop_train.setEnabled(False)
        self.state_tool_tip = None

        self._train_param = TrainParameter()
        self._connect_signals_and_slot()

        self.model_thread = None
        self._train_finished = True
        self._resume = False
        self._last_model = ""

    def _connect_signals_and_slot(self):
        self.btn_start_train.clicked.connect(self._on_start_train_clicked)
        self.btn_stop_train.clicked.connect(self._on_stop_train_clicked)

    @Slot(TrainParameter)
    def _on_train_param_changed(self, train_param: TrainParameter):
        self._train_param = train_param
        self.psb_train.set_max_value(int(self._train_param.epoch))

    def _on_model_status_changed(self, model_name, use_pretrain):
        self._current_model_name = model_name
        self._use_pretrain = use_pretrain

    def _initial_model(self):
        with open(r"C:\Users\84945\Desktop\ultralytics_workspace\project\P000000\T000000\train_config.yaml", "r", encoding="utf8") as f:
            s = yaml.safe_load(f)
        self.model_thread = ModelTrainThread(**s)
        self._train_finished = False
        self.model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
        self.model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
        self.model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
        self.model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
        self.model_thread.train_end_signal.connect(self.on_handle_train_end)

        self.stop_train_model_signal.connect(self.model_thread.stop_train)

    def _turn_widget_enable_status(self):

        # train interface
        self.btn_start_train.setEnabled(not self.btn_start_train.isEnabled())
        self.btn_stop_train.setEnabled(not self.btn_stop_train.isEnabled())

    @Slot()
    def _on_start_train_clicked(self):

        if not self._train_finished:
            self._resume = True
        if self._resume and self._last_model:
            self._current_model_name = self._last_model
            log_warning(f"{self.tr('model will resume to train, last model is: ')}{self._last_model}")
        else:
            self._resume = False
        self._initial_model()
        self._turn_widget_enable_status()

        # 设置状态工具栏并显示
        self.state_tool_tip = StateToolTip(
            self.tr('The model is currently being trained '), self.tr('Please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()

        self.model_thread.start()

    @Slot()
    def _on_stop_train_clicked(self):
        self.stop_train_model_signal.emit()
        self.model_thread.quit()
        self.model_thread.wait()
        self._turn_widget_enable_status()
        # 立即刷新界面
        QCoreApplication.processEvents()
        self.ted_train_log.append(
            log_warning(f"model training stopped by user, click start training to resume training process"))

    @Slot(str)
    def on_handle_epoch_start(self, split: str):
        self.ted_train_log.append(format_log(split, color="#0b80e0"))

    @Slot(str)
    def on_handle_batch_end(self, metrics: str):
        self.ted_train_log.append(format_log(metrics, color="#0b80e0"))

    @Slot(int, str)
    def on_handle_epoch_end(self, epoch: int, last_model: str):
        self._last_model = last_model
        self.psb_train.set_value(epoch)

    @Slot(str)
    def on_handle_fit_epoch_end(self, format_metrics: str):
        self.ted_train_log.append(format_log(format_metrics, color="#0b80e0"))

    @Slot(int)
    def on_handle_train_end(self, cur_epoch: int):
        self._turn_widget_enable_status()
        self._train_finished = True
        if cur_epoch == int(self._train_param.epoch):
            self.ted_train_log.append(log_info(f"{self.tr('train finished')} epoch = {cur_epoch}"))
        else:
            self.ted_train_log.append(log_info(f"{self.tr('train finished ahead of schedule')} epoch = {cur_epoch}"))
        # 数据转换完成，显示状态信息
        self.state_tool_tip.setContent(
            self.tr('Model training is completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
