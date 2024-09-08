from pathlib import Path

import yaml
from PySide6.QtCore import Slot, Signal, QCoreApplication
from PySide6.QtGui import QTextCursor, QFont
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout)
from qfluentwidgets import PushButton, PrimaryPushButton, FluentIcon, \
    TextEdit, StateToolTip

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_process_bar import CustomProcessBar
from common.db_helper import db_session
from common.utils import log_info, log_warning, format_log
from home.task.model_trainer_thread.classify_trainer_thread import ModelTrainThread
from home.types import TaskInfo, TaskStatus
from model_train.train_parameter_widget import TrainParameter
from models.models import Task


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

        self.ted_train_log = TextEdit()
        font = QFont("Courier")  # "Courier" 是常见的等宽字体
        font.setWeight(QFont.Weight.Normal)
        font.setPixelSize(14)
        font.setStyleHint(QFont.StyleHint.Monospace)  # 设置字体风格提示为 Monospace (等宽字体)
        self.ted_train_log.setFont(font)
        self.ted_train_log.setReadOnly(True)
        self.ted_train_log.setMinimumHeight(400)

        self.vly.addLayout(self.hly_btn)
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

    def _connect_signals_and_slot(self):
        self.btn_start_train.clicked.connect(self._on_start_train_clicked)
        self.btn_stop_train.clicked.connect(self._on_stop_train_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
        if task_info.task_status.value >= TaskStatus.CFG_FINISHED.value:
            self._train_config_file_path = task_info.task_dir / "train_config.yaml"
            with open(self._train_config_file_path, "r", encoding="utf8") as f:
                self._train_parameter = yaml.safe_load(f)
            self.psb_train.set_max_value(self._train_parameter["epochs"])

    def _initial_model(self):
        self.model_thread = ModelTrainThread(self._train_parameter)
        self._train_finished = False
        self.model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
        self.model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
        self.model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
        self.model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
        self.model_thread.train_end_signal.connect(self.on_handle_train_end)

        self.stop_train_model_signal.connect(self.model_thread.stop_train)

    def _turn_widget_enable_status(self):
        self.btn_start_train.setEnabled(not self.btn_start_train.isEnabled())
        self.btn_stop_train.setEnabled(not self.btn_stop_train.isEnabled())

    @Slot()
    def _on_start_train_clicked(self):
        if self._task_info.task_status == TaskStatus.TRAINING and not self._train_finished:
            with open(self._train_config_file_path, "w", encoding="utf8") as f:
                if self._last_model:
                    self._train_parameter["resume"] = True
                    self._train_parameter["model"] = self._last_model
                    yaml.dump(self._train_parameter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            log_warning(f"{self.tr('model will resume to train, last model is: ')}{self._last_model}")
        self._initial_model()
        self._turn_widget_enable_status()

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

        cursor = self.ted_train_log.textCursor()

        # 获取 QTextEdit 的文本内容
        document = self.ted_train_log.document()

        # 获取最后一行的行号
        last_block = document.lastBlock()

        # 获取最后一行的内容
        last_line_text = last_block.text()

        # 如果最后一行有内容，则删除最后一行
        if last_line_text:
            cursor.movePosition(cursor.MoveOperation.End)  # 移动到文本末尾
            cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)  # 选择最后一行
            cursor.removeSelectedText()

            # 删除末尾的换行符
            cursor.deletePreviousChar()

        self.ted_train_log.setTextCursor(cursor)
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
        if cur_epoch == self._train_parameter["epochs"]:
            self.ted_train_log.append(log_info(f"{self.tr('train finished')} epoch = {cur_epoch}"))
        else:
            self.ted_train_log.append(log_info(f"{self.tr('train finished ahead of schedule')} epoch = {cur_epoch}"))
        # 数据转换完成，显示状态信息
        self.state_tool_tip.setContent(
            self.tr('Model training is completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
