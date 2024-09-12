import pickle
from pathlib import Path

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
from home.types import TaskInfo, TaskStatus
from models.models import Task
from settings import cfg


class ModelExportWidget(CollapsibleWidgetItem):
    is_training_signal = Signal(bool)

    def __init__(self, parent=None):
        super(ModelExportWidget, self).__init__(self.tr("▌Model export"), parent=parent)
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

        self._loss_plots = dict()
        self._metric_plots = dict()

        self.vly.addLayout(self.hly_btn)

        self.btn_stop_train.setEnabled(False)
        self.state_tool_tip = None

        self._connect_signals_and_slot()
        self._train_parameter: dict = dict()
        self._train_config_file_path: Path | None = None
        self.model_thread = None
        self._last_model = ""
        self._task_info: TaskInfo | None = None

        self._loss_data = dict()
        self._metric_data = dict()

        self._is_resume = False

    def _connect_signals_and_slot(self):
        pass

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
