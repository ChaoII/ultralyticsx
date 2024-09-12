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
    is_training_signal = Signal(bool)
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

        self._loss_data = dict()
        self._metric_data = dict()

        self._task_thread_map = TaskThreadMap()

        self._is_resume = False

    def _connect_signals_and_slot(self):
        self.btn_start_train.clicked.connect(self._on_start_train_clicked)
        self.btn_stop_train.clicked.connect(self._on_stop_train_clicked)
        self.btn_next_step.clicked.connect(self._on_next_step_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self.ted_train_log.clear()
        self.pg_widget.clear()
        self.btn_next_step.setVisible(False)
        self._loss_data = dict()
        self._metric_data = dict()
        self._task_info = task_info
        self.ted_train_log.set_log_path(self._task_info.task_dir / "train_log.txt")
        if task_info.task_status.value >= TaskStatus.CFG_FINISHED.value:
            self._train_config_file_path = task_info.task_dir / "train_config.yaml"
            with open(self._train_config_file_path, "r", encoding="utf8") as f:
                self._train_parameter = yaml.safe_load(f)
            self.psb_train.set_max_value(self._train_parameter["epochs"])
        if TaskStatus.TRAINING.value <= task_info.task_status.value != TaskStatus.TRN_FINISHED.value:
            log_file_path = self._task_info.task_dir / "train_log.txt"
            if log_file_path.exists():
                with open(log_file_path, "r", encoding="utf8") as f:
                    self.ted_train_log.setPlainText(f.read())
                    v_scroll_bar = self.ted_train_log.verticalScrollBar()
                    v_scroll_bar.setValue(v_scroll_bar.maximum())
            # 加载训练历史数据
            train_history_path = self._task_info.task_dir / "train_history"
            if train_history_path.exists():
                train_history = pickle.load(open(train_history_path, "rb"))
                self._loss_data, self._metric_data = train_history
                self.load_graph()

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

        if task_info.task_status == TaskStatus.TRAINING:
            if task_info.task_id in self._task_thread_map.get_thread_map():
                if not self._task_thread_map.get_thread_by_task_id(task_info.task_id).isRunning():
                    task_thread = self._initial_model_thread()
                    if task_thread:
                        self._task_thread_map.update_thread({task_info.task_id: task_thread})
            else:
                log_error("TaskStatus is TRAINING, but task thread not existed")
        else:
            if task_info.task_id not in self._task_thread_map.get_thread_map():
                task_thread = self._initial_model_thread()
                if task_thread:
                    self._task_thread_map.update_thread({task_info.task_id: task_thread})

    def _initial_model_thread(self) -> Optional[ModelTrainThread]:
        model_thread = ModelTrainThread(self._train_parameter)
        model_thread.train_start_signal.connect(self.on_handle_train_start)
        model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
        model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
        model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
        model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
        model_thread.train_end_signal.connect(self.on_handle_train_end)
        model_thread.model_train_failed.connect(self._on_model_train_failed)
        if model_thread.init_model_trainer():
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

        self._disable_btn_to_train_status()
        # 设置状态工具栏并显示
        self.state_tool_tip = StateToolTip(
            self.tr('The model is currently being trained '), self.tr('Please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()

        self._task_thread_map.get_thread_by_task_id(self._task_info.task_id).start()
        self._task_info.task_status = TaskStatus.TRAINING
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = self._task_info.task_status.value
        if self._task_info.task_status != TaskStatus.TRN_FINISHED:
            self.btn_next_step.setVisible(False)

    @Slot()
    def _on_start_train_clicked(self):
        self.start_train()

    @Slot()
    def _on_stop_train_clicked(self):
        self._task_thread_map.get_thread_by_task_id(self._task_info.task_id).stop_train()
        self._task_thread_map.get_thread_by_task_id(self._task_info.task_id).quit()
        self._task_thread_map.get_thread_by_task_id(self._task_info.task_id).wait()
        # 立即刷新界面
        QCoreApplication.processEvents()
        self.ted_train_log.append(
            log_warning(self.tr("model training stopped by user, click start training to resume training process")))

    @Slot()
    def _on_next_step_clicked(self):
        self.next_step_clicked.emit(self._task_info)

    def load_graph(self):
        self.pg_widget.clear()
        for key, value in self._loss_data.items():
            self._loss_plots[key] = self.pg_widget.addPlot(title=key)
            self._loss_plots[key].showGrid(x=True, y=True)
            self._loss_plots[key].showAxes(True, showValues=(True, False, False, True))
            self._loss_plots[key].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self._loss_plots[key].plot(self._loss_data[key], name=key)
        self.pg_widget.nextRow()
        for key, value in self._metric_data.items():
            self._metric_plots[key] = self.pg_widget.addPlot(title=key)
            self._metric_plots[key].showGrid(x=True, y=True)
            self._metric_plots[key].showAxes(True, showValues=(True, False, False, True))
            self._metric_plots[key].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self._metric_plots[key].plot(self._metric_data[key], name=key)

    @Slot(dict)
    def on_handle_train_start(self, metrics: dict, loss_names: list):
        if self._task_info.task_status.value <= TaskStatus.TRAINING.value and not self._loss_data:
            for loss_name in loss_names:
                self._loss_data[loss_name] = []
            for key, value in metrics.items():
                self._metric_data[key] = []
        self.load_graph()
        self.is_training_signal.emit(True)

    @Slot(str)
    def on_handle_epoch_start(self, split: str):
        self.ted_train_log.append(split)

    @Slot(str, float)
    def on_handle_batch_end(self, metrics: str, loss_items: dict):
        for key, value in loss_items.items():
            self._loss_data[key].append(value)
            self._loss_plots[key].plot(self._loss_data[key], name=key)
        self.ted_train_log.append(metrics)

    @Slot(int, str)
    def on_handle_epoch_end(self, epoch: int, last_model: str):
        self._last_model = last_model
        self.psb_train.set_value(epoch)
        self.ted_train_log.save_to_log()
        # 保存训练历史记录（loss,metrics）
        pickle.dump([self._loss_data, self._metric_data], open(self._task_info.task_dir / "train_history", "wb"))

    @Slot(str, dict)
    def on_handle_fit_epoch_end(self, format_metrics: str, metrics: dict):
        self.ted_train_log.append(format_metrics)
        for key, value in metrics.items():
            self._metric_data[key].append(value)
            self._metric_plots[key].plot(self._metric_data[key], name=key)

    @Slot(int, bool)
    def on_handle_train_end(self, cur_epoch: int, manual_stop: bool):
        self._enable_btn_to_train_status()
        if cur_epoch == self._train_parameter["epochs"] and not manual_stop:
            self.ted_train_log.append(log_info(f"{self.tr('train finished')} epoch = {cur_epoch}"))
            self._task_info.task_status = TaskStatus.TRN_FINISHED
            self._train_parameter["resume"] = ""
            self.btn_start_train.setText(self.tr("Retrain"))
        else:
            self.ted_train_log.append(log_info(f"{self.tr('train finished ahead of schedule')} epoch = {cur_epoch}"))
            self._task_info.task_status = TaskStatus.TRN_PAUSE
            if self._last_model:
                self._train_parameter["resume"] = self._last_model
        with open(self._train_config_file_path, "w", encoding="utf8") as f:
            yaml.dump(self._train_parameter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
            task.task_status = self._task_info.task_status.value
        # 数据转换完成，显示状态信息
        self.state_tool_tip.setContent(
            self.tr('Model training is completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
        self.ted_train_log.save_to_log()

        self.is_training_signal.emit(False)

    @Slot(str)
    def _on_model_train_failed(self, error_info: str):
        self.ted_train_log.append(log_error(error_info))
        self.ted_train_log.save_to_log()
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
        self.is_training_signal.emit(False)
