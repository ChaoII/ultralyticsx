from pathlib import Path

import yaml
from PySide6.QtCore import Slot, Signal, QCoreApplication
from PySide6.QtGui import QTextCursor, QFont, QColor
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy)
from pyqtgraph import PlotItem
from qfluentwidgets import PushButton, PrimaryPushButton, FluentIcon, \
    TextEdit, StateToolTip, FluentStyleSheet
import pyqtgraph as pg

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_process_bar import CustomProcessBar
from common.db_helper import db_session
from common.utils import log_info, log_warning, format_log, log_error
from home.task.model_trainer_thread.classify_trainer_thread import ModelTrainThread
from home.types import TaskInfo, TaskStatus
from model_train.train_parameter_widget import TrainParameter
from models.models import Task
from common.utils import logger


class RichTextLogWidget(TextEdit):
    def __init__(self, save_file_path: Path | None = None, parent=None):
        super().__init__(parent=parent)
        self._save_file_path = save_file_path

    def set_log_path(self, log_path: Path):
        self._save_file_path = log_path

    def save_to_log(self, save_file_path: Path | None = None):
        if save_file_path:
            with open(self._save_file_path, "w", encoding="utf8") as f:
                f.write(self.toPlainText())
        else:
            if self._save_file_path:
                with open(self._save_file_path, "w", encoding="utf8") as f:
                    f.write(self.toPlainText())
            else:
                raise EOFError(self.tr("save to log must point a file path"))


class ModelTrainWidget(CollapsibleWidgetItem):
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

        pg.setConfigOptions(antialias=True)
        self.pg_widget = pg.GraphicsLayoutWidget(show=False)
        self.pg_widget.setBackground(QColor("#2f3441"))
        self.pg_widget.setFixedHeight(300)

        self._loss_plots = dict()
        self._metric_plots = dict()

        self.ted_train_log = RichTextLogWidget()
        font = QFont("Courier")  # "Courier" 是常见的等宽字体
        font.setWeight(QFont.Weight.Normal)
        font.setPixelSize(14)
        font.setStyleHint(QFont.StyleHint.Monospace)  # 设置字体风格提示为 Monospace (等宽字体)
        self.ted_train_log.setFont(font)
        self.ted_train_log.setReadOnly(True)
        self.ted_train_log.setMinimumHeight(450)

        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.pg_widget)
        self.vly.addWidget(self.ted_train_log)

        self.btn_stop_train.setEnabled(False)
        self.state_tool_tip = None

        self._connect_signals_and_slot()
        self._train_parameter: dict = dict()
        self._train_config_file_path: Path | None = None
        self.model_thread = None
        self._train_finished = True
        self._resume = False
        self._last_model = ""
        self._task_info: TaskInfo | None = None

        self._loss_data = dict()
        self._metric_data = dict()

        self._train_step = 0

    def _connect_signals_and_slot(self):
        self.btn_start_train.clicked.connect(self._on_start_train_clicked)
        self.btn_stop_train.clicked.connect(self._on_stop_train_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
        self.ted_train_log.set_log_path(self._task_info.task_dir / "train_log.txt")
        if task_info.task_status.value >= TaskStatus.CFG_FINISHED.value:
            self._train_config_file_path = task_info.task_dir / "train_config.yaml"
            with open(self._train_config_file_path, "r", encoding="utf8") as f:
                self._train_parameter = yaml.safe_load(f)
            self.psb_train.set_max_value(self._train_parameter["epochs"])
        if task_info.task_status.value > TaskStatus.TRAINING.value:
            log_file_path = self._task_info.task_dir / "train_log.txt"
            if not log_file_path.exists():
                return
            with open(log_file_path, "r", encoding="utf8") as f:
                self.ted_train_log.setPlainText(f.read())
                v_scroll_bar = self.ted_train_log.verticalScrollBar()
                v_scroll_bar.setValue(v_scroll_bar.maximum())

        if task_info.task_status == TaskStatus.TRAINING:
            self.btn_start_train.setEnabled(False)
            self.btn_stop_train.setEnabled(True)
        # 如果
        if task_info.task_status.value > TaskStatus.TRAINING.value:
            self.btn_start_train.setEnabled(True)
            self.btn_stop_train.setEnabled(False)
            self.btn_start_train.setText(self.tr("Resume train"))
        if task_info.task_status == TaskStatus.TRN_FINISHED:
            self.btn_start_train.setText(self.tr("Retrain"))

    def _initial_model(self):
        self.model_thread = ModelTrainThread(self._train_parameter)

        self.model_thread.train_start_signal.connect(self.on_handle_train_start)
        self.model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
        self.model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
        self.model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
        self.model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
        self.model_thread.train_end_signal.connect(self.on_handle_train_end)
        self.model_thread.model_train_failed.connect(self._on_model_train_failed)
        self.stop_train_model_signal.connect(self.model_thread.stop_train)
        self.model_thread.init_model_trainer()
        self._train_finished = False

    def _enable_btn_to_train_status(self):
        self.btn_start_train.setEnabled(True)
        self.btn_stop_train.setEnabled(False)

    def _disable_btn_to_train_status(self):
        self.btn_start_train.setEnabled(False)
        self.btn_stop_train.setEnabled(True)

    def start_train(self):
        with open(self._train_config_file_path, "r", encoding="utf8") as f:
            self._train_parameter = yaml.safe_load(f)

        # todo 清空graphics
        self.ted_train_log.clear()
        self._initial_model()
        self._disable_btn_to_train_status()
        # 设置状态工具栏并显示
        self.state_tool_tip = StateToolTip(
            self.tr('The model is currently being trained '), self.tr('Please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()

        self.model_thread.start()
        self._task_info.task_status = TaskStatus.TRAINING
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = self._task_info.task_status.value

    @Slot()
    def _on_start_train_clicked(self):
        if self._task_info.task_status.value >= TaskStatus.TRAINING.value and not self._train_finished:
            with open(self._train_config_file_path, "w", encoding="utf8") as f:
                if self._last_model:
                    self._train_parameter["resume"] = self._last_model
                    yaml.dump(self._train_parameter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            log_warning(f"{self.tr('model will resume to train, last model is: ')}{self._last_model}")
        self.start_train()

    @Slot()
    def _on_stop_train_clicked(self):
        self.model_thread.stop_train()
        self.model_thread.quit()
        self.model_thread.wait()
        # 立即刷新界面
        QCoreApplication.processEvents()
        self.ted_train_log.append(
            log_warning(self.tr("model training stopped by user, click start training to resume training process")))

    @Slot(dict)
    def on_handle_train_start(self, metrics: dict, loss_names: list):

        for loss_name in loss_names:
            self._loss_data[loss_name] = []
            self._loss_plots[loss_name] = self.pg_widget.addPlot(title=loss_name)
            self._loss_plots[loss_name].showGrid(x=False, y=False)
            # self._loss_plots[loss_name].setLabel("left", "loss")
            self._loss_plots[loss_name].showAxes(True, showValues=(True, False, False, True))
            self._loss_plots[loss_name].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        for key, value in metrics.items():
            self._metric_data[key] = []
            self._metric_plots[key] = self.pg_widget.addPlot(title=key)
            self._metric_plots[key].showGrid(x=False, y=False)
            self._metric_plots[key].showAxes(True, showValues=(True, False, False, True))
            self._metric_plots[key].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    @Slot(str)
    def on_handle_epoch_start(self, split: str):
        self.ted_train_log.append(split)

    @Slot(str, float)
    def on_handle_batch_end(self, metrics: str, loss_items: dict):
        for key, value in loss_items.items():
            self._loss_data[key].append(value)
            self._loss_plots[key].plot(self._loss_data[key], pen=(255, 0, 0), name=key)
        self.ted_train_log.append(metrics)

    @Slot(int, str)
    def on_handle_epoch_end(self, epoch: int, last_model: str):
        self._last_model = last_model
        self.psb_train.set_value(epoch)
        self.ted_train_log.save_to_log()

    @Slot(str, dict)
    def on_handle_fit_epoch_end(self, format_metrics: str, metrics: dict):
        self.ted_train_log.append(format_metrics)
        for key, value in metrics.items():
            self._metric_data[key].append(value)
            self._metric_plots[key].plot(self._metric_data[key], pen=(255, 0, 0), name=key)

    @Slot(int)
    def on_handle_train_end(self, cur_epoch: int):
        self._enable_btn_to_train_status()
        self._train_finished = True
        if cur_epoch == self._train_parameter["epochs"]:
            self.ted_train_log.append(log_info(f"{self.tr('train finished')} epoch = {cur_epoch}"))
            self._task_info.task_status = TaskStatus.TRN_FINISHED
        else:
            self.ted_train_log.append(log_info(f"{self.tr('train finished ahead of schedule')} epoch = {cur_epoch}"))
            self._task_info.task_status = TaskStatus.TRN_PAUSE
            self._train_finished = False
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = self._task_info.task_status.value
        # 数据转换完成，显示状态信息
        self.state_tool_tip.setContent(
            self.tr('Model training is completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
        self.ted_train_log.save_to_log()

    @Slot(str)
    def _on_model_train_failed(self, error_info: str):
        self.ted_train_log.append(log_error(error_info))
        self.ted_train_log.save_to_log()
