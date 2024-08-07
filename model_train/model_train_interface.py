from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip

from utils.utils import log_info, log_warning, format_log
from .model_info_widget import ModelInfoCard
from .train_parameter_widget import ModelTrainParamCard, TrainParameter
from .trainer import ModelTrainThread


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
        self.vly = QVBoxLayout(self)

        self.spliter = QSplitter(Qt.Orientation.Vertical, self)
        self.vly.addWidget(self.spliter)
        self.widget_top = QWidget()

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

        self.widget_bottom = QWidget()
        vly_train_log = QVBoxLayout(self.widget_bottom)
        vly_train_log.addWidget(self.ted_train_log)

        v_layout = QVBoxLayout(self.widget_top)
        v_layout.addWidget(self.model_info_card)
        v_layout.addWidget(self.model_train_param_card)
        v_layout.addLayout(gly_btn)

        self.spliter.addWidget(self.widget_top)
        self.spliter.addWidget(self.widget_bottom)
        self.spliter.setStretchFactor(1, 1)
        self.spliter.setHandleWidth(1)

        self.btn_stop_train.setEnabled(False)
        self.state_tool_tip = None

        self._train_param = TrainParameter()
        self._connect_signals_and_slot()

        self._current_model_name = ""
        self._use_pretrain = False
        self.model_thread = None
        self._train_finished = True
        self._resume = False
        self._last_model = ""

    def _connect_signals_and_slot(self):
        self.model_train_param_card.train_param_changed.connect(self._on_train_param_changed)
        self.model_info_card.model_status_changed.connect(self._on_model_status_changed)
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
        self.model_thread = ModelTrainThread(self._current_model_name,
                                             self._use_pretrain,
                                             self._train_param.dataset_config,
                                             self._train_param.epoch,
                                             self._train_param.batch_size,
                                             self._train_param.learning_rate,
                                             self._train_param.workers,
                                             self._resume)
        self._train_finished = False
        self.model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
        self.model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
        self.model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
        self.model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
        self.model_thread.train_end_signal.connect(self.on_handle_train_end)

        self.stop_train_model_signal.connect(self.model_thread.stop_train)

    def _turn_widget_enable_status(self):
        # model info card
        self.model_info_card.cmb_model_type.setEnabled(not self.model_info_card.cmb_model_type.isEnabled())
        self.model_info_card.cmb_model_name.setEnabled(not self.model_info_card.cmb_model_name.isEnabled())
        self.model_info_card.ckb_use_pretrain_model.setEnabled(
            not self.model_info_card.ckb_use_pretrain_model.isEnabled())

        # model train parameter card
        self.model_train_param_card.btn_load_dataset_config.setEnabled(
            not self.model_train_param_card.btn_load_dataset_config.isEnabled())
        self.model_train_param_card.sp_epoch.setEnabled(not self.model_train_param_card.sp_epoch.isEnabled())
        self.model_train_param_card.sp_batch_size.setEnabled(not self.model_train_param_card.sp_batch_size.isEnabled())
        self.model_train_param_card.dsp_learning_rate.setEnabled(
            not self.model_train_param_card.dsp_learning_rate.isEnabled())
        self.model_train_param_card.sp_workers.setEnabled(not self.model_train_param_card.sp_workers.isEnabled())
        self.model_train_param_card.led_dataset_config.setEnabled(
            not self.model_train_param_card.led_dataset_config.isEnabled())

        # train interface
        self.btn_start_train.setEnabled(not self.btn_start_train.isEnabled())
        self.btn_stop_train.setEnabled(not self.btn_stop_train.isEnabled())

    @Slot()
    def _on_start_train_clicked(self):
        self.ted_train_log.append(
            log_info(f"{self.tr('model ')}{self._current_model_name}{self.tr(' start training')}"))
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
