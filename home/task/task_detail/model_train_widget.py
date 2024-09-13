import pickle
from pathlib import Path
from typing import Optional

import pyqtgraph as pg
import yaml
from PySide6.QtCore import Slot, QCoreApplication, Signal
from PySide6.QtGui import QFont, QColor, Qt
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy)
from pyqtgraph import PlotItem
from qfluentwidgets import PushButton, PrimaryPushButton, FluentIcon, \
    TextEdit, StateToolTip, isDarkTheme, InfoBar, InfoBarPosition

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_process_bar import CustomProcessBar
from common.db_helper import db_session
from common.utils import log_info, log_warning, log_error
from home.task.model_trainer_thread.classify_trainer_thread import ModelTrainThread
from home.task.task_threads import TaskThreadMap
from home.types import TaskInfo, TaskStatus
from models.models import Task
from settings import cfg


class GraphicsLayoutWidget(pg.GraphicsLayoutWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pg.setConfigOptions(antialias=True)
        cfg.themeChanged.connect(self._on_theme_changed)
        self._background_colors: list[QColor] = [QColor("#ffffff"), QColor("#2f3441")]

    def set_background(self, light_color, dark_color):
        self._background_colors = [light_color, dark_color]

    def _on_theme_changed(self):
        if isDarkTheme():
            self.setBackground(self._background_colors[1])
        else:
            self.setBackground(self._background_colors[0])

    def addPlot(self, *args, **kwargs) -> PlotItem:
        return super().addPlot(*args, **kwargs)

    def nextRow(self, *args, **kwargs):
        super().nextRow(*args, **kwargs)

    def clear(self):
        super().clear()


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
    is_training_signal = Signal(bool, str)
    next_step_clicked = Signal(TaskInfo)

    def __init__(self, parent=None):
        super(ModelTrainWidget, self).__init__(self.tr("▌Model training"), parent=parent)
        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)
        self.vly = QVBoxLayout(self.content_widget)
        self.vly.setContentsMargins(20, 0, 20, 0)
        self.set_content_widget(self.content_widget)

        self.btn_start_train = PrimaryPushButton(FluentIcon.PLAY, self.tr("Start train"))
        self.btn_stop_train = PushButton(FluentIcon.PAUSE, self.tr("Stop train"))
        self.btn_next_step = PushButton(FluentIcon.RINGER, self.tr("Next step"))
        self.btn_next_step.setVisible(False)
        self.btn_stop_train.setEnabled(False)
        self.psb_train = CustomProcessBar()
        self.psb_train.set_value(0)
        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_start_train)
        self.hly_btn.addWidget(self.btn_stop_train)
        self.hly_btn.addWidget(self.btn_next_step)
        self.hly_btn.addWidget(self.psb_train)

        pg.setConfigOptions(antialias=True)
        self.pg_widget = GraphicsLayoutWidget(show=False)
        self.pg_widget.setBackground(QColor("#2f3441"))
        self.pg_widget.setFixedHeight(600)
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

        self.state_tool_tip = None

        self._connect_signals_and_slot()
        self._train_parameter: dict = dict()
        self._train_config_file_path: Path | None = None
        self._last_model = ""
        self._task_info: TaskInfo | None = None

        self._task_thread_map = TaskThreadMap()
        self._current_thread: ModelTrainThread | None = None

    def _connect_signals_and_slot(self):
        self.btn_start_train.clicked.connect(self._on_start_train_clicked)
        self.btn_stop_train.clicked.connect(self._on_stop_train_clicked)
        self.btn_next_step.clicked.connect(self._on_next_step_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
        if task_info.task_status.value < TaskStatus.CFG_FINISHED.value:
            return
        self.ted_train_log.clear()
        self.pg_widget.clear()
        self.btn_next_step.setVisible(False)
        if task_info.task_status.value >= TaskStatus.CFG_FINISHED.value:
            self._train_config_file_path = task_info.task_dir / "train_config.yaml"
            self._train_parameter = yaml.safe_load(open(self._train_config_file_path, "r", encoding="utf8"))
            self.psb_train.set_max_value(self._train_parameter["epochs"])
            log_file_path = self._task_info.task_dir / "train.log"
            if log_file_path.exists():
                self.ted_train_log.setPlainText(open(log_file_path, "r", encoding="utf8").read())
                v_scroll_bar = self.ted_train_log.verticalScrollBar()
                v_scroll_bar.setValue(v_scroll_bar.maximum())
            # 加载训练历史数据
            train_loss_path = self._task_info.task_dir / "train_loss"
            train_metric_path = self._task_info.task_dir / "train_metric"

            if train_loss_path.exists() and train_metric_path.exists():
                train_loss = pickle.load(open(train_loss_path, "rb"))
                train_metric = pickle.load(open(train_metric_path, "rb"))
                self.psb_train.set_value(len(list(train_metric.values())[1]))
                self.load_graph(train_loss, train_metric)

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
            self.btn_next_step.setVisible(True)

    def _initial_model_thread(self) -> Optional[ModelTrainThread]:
        model_thread = ModelTrainThread(self._train_parameter)
        model_thread.train_start_signal.connect(self.on_handle_train_start)
        model_thread.train_epoch_end.connect(self.on_handle_epoch_end)
        model_thread.model_train_end.connect(self.on_handle_train_end)
        model_thread.model_train_failed.connect(self._on_model_train_failed)
        model_thread.log_changed_signal.connect(self._on_log_changed)
        model_thread.loss_changed_signal.connect(self._on_loss_changed)
        model_thread.metric_changed_signal.connect(self._on_metric_changed)
        if model_thread.init_model_trainer(self._task_info):
            return model_thread
        else:
            return None

    def _enable_btn_to_train_status(self):
        self.btn_start_train.setEnabled(True)
        self.btn_stop_train.setEnabled(False)

    def _disable_btn_to_train_status(self):
        self.btn_start_train.setEnabled(False)
        self.btn_stop_train.setEnabled(True)

    def start_train(self):
        self.set_task_info(self._task_info)
        if self._task_info.task_status == TaskStatus.TRAINING:
            if self._task_info.task_id in self._task_thread_map.get_thread_map():
                self._current_thread = self._task_thread_map.get_thread_by_task_id(self._task_info.task_id)
            else:
                log_error("status is training but not find the train thread")
                return
        else:
            if self._task_info.task_id not in self._task_thread_map.get_thread_map():
                task_thread = self._initial_model_thread()
                if task_thread:
                    self._task_thread_map.update_thread({self._task_info.task_id: task_thread})
                    self._current_thread = self._task_thread_map.get_thread_by_task_id(self._task_info.task_id)

        self._disable_btn_to_train_status()
        # 设置状态工具栏并显示
        self.state_tool_tip = StateToolTip(
            self.tr('The model is currently being trained '), self.tr('Please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()
        self._current_thread.start()
        self._task_info.task_status = TaskStatus.TRAINING
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = self._task_info.task_status.value
        if self._task_info.task_status != TaskStatus.TRN_FINISHED:
            self.btn_next_step.setVisible(False)

    @Slot(str)
    def _on_log_changed(self, message: str):
        if self.sender() != self._current_thread:
            return
        self.ted_train_log.append(message)

    @Slot(dict)
    def _on_loss_changed(self, loss_data: dict):
        if self.sender() != self._current_thread:
            return
        for key, value in loss_data.items():
            self._loss_plots[key].plot(value, name=key)

    @Slot(dict)
    def _on_metric_changed(self, metric_data: dict):
        if self.sender() != self._current_thread:
            return
        for key, value in metric_data.items():
            self._metric_plots[key].plot(value, name=key)

    @Slot()
    def _on_start_train_clicked(self):
        self.start_train()

    @Slot()
    def _on_stop_train_clicked(self):
        self._current_thread.stop_train()
        self._current_thread.quit()
        self._current_thread.wait()
        # 立即刷新界面
        QCoreApplication.processEvents()
        self.ted_train_log.append(
            log_warning(self.tr("model training stopped by user, click start training to resume training process")))

    @Slot()
    def _on_next_step_clicked(self):
        self.next_step_clicked.emit(self._task_info)

    def load_graph(self, loss_data: dict, metric_data: dict):
        self.pg_widget.clear()
        for key, value in loss_data.items():
            self._loss_plots[key] = self.pg_widget.addPlot(title=key)
            self._loss_plots[key].showGrid(x=True, y=True)
            self._loss_plots[key].showAxes(True, showValues=(True, False, False, True))
            self._loss_plots[key].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self._loss_plots[key].plot(loss_data[key], name=key)
        self.pg_widget.nextRow()
        for key, value in metric_data.items():
            self._metric_plots[key] = self.pg_widget.addPlot(title=key)
            self._metric_plots[key].showGrid(x=True, y=True)
            self._metric_plots[key].showAxes(True, showValues=(True, False, False, True))
            self._metric_plots[key].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self._metric_plots[key].plot(metric_data[key], name=key)

    @Slot(dict)
    def on_handle_train_start(self, loss_data: dict, metric_data: dict):
        if self.sender() != self._current_thread:
            return
        self.load_graph(loss_data, metric_data)
        self.is_training_signal.emit(True, self._task_info.task_id)

    @Slot(int, str)
    def on_handle_epoch_end(self, epoch: int):
        if self.sender() != self._current_thread:
            return
        self._last_model = self._current_thread.get_last_model()
        self.psb_train.set_value(epoch)
        # 保存训练历史记录（loss,metrics）

    @Slot(TaskInfo)
    def on_handle_train_end(self, task_info: TaskInfo):
        if self.sender() == self._current_thread:
            self._enable_btn_to_train_status()
            if task_info.task_status == TaskStatus.TRN_FINISHED:
                self.btn_start_train.setText(self.tr("ReTrain"))
            if task_info.task_status == TaskStatus.TRN_PAUSE:
                self.btn_start_train.setText(self.tr("Resume"))

            # 数据转换完成，显示状态信息
            self.state_tool_tip.setContent(
                self.tr('Model training is completed!') + ' 😆')
            self.state_tool_tip.setState(True)
            self.state_tool_tip = None
            self.is_training_signal.emit(False, self._task_info.task_id)

        with open(task_info.task_dir / "train_config.yaml", "w", encoding="utf8") as f:
            yaml.dump(self.sender().get_train_parameters(), f, default_flow_style=False, allow_unicode=True,
                      sort_keys=False)
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=task_info.task_id).first()
            task.task_status = task_info.task_status.value

    @Slot(str)
    def _on_model_train_failed(self, error_info: str):
        if self.sender() != self._current_thread:
            return
        self.ted_train_log.append(log_error(error_info))
        self._enable_btn_to_train_status()
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
        self._task_info.task_status = TaskStatus.TRAIN_FAILED
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = self._task_info.task_status.value

        InfoBar.error(
            title='',
            content=self.tr("Model train failed"),
            orient=Qt.Orientation.Vertical,  # 内容太长时可使用垂直布局
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=-1,
            parent=self.parent().parent()
        )
        self.is_training_signal.emit(False, self._task_info.task_id)
