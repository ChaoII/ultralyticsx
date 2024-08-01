from qfluentwidgets import HeaderCardWidget, BodyLabel, ComboBox, CheckBox, LineEdit, PrimaryPushButton, FluentIcon, \
    LineEditButton
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Slot, Signal, Qt
from .options import *


class TrainParameter:
    epoch: int = 0
    batch_size: int = 0
    learning_rate: float = 0.0
    works: int = 0


class ModelTrainParamCard(HeaderCardWidget):
    """ Model information card """
    # model name and is use pretrain model
    train_param_changed = Signal(TrainParameter)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("model training parameter"))

        self.dataset_lbl = BodyLabel(self.tr('dataset config file path: '), self)
        self.dataset_config_led = LineEdit()
        self.dataset_config_led.setPlaceholderText(self.tr("please select a dataset config file"))
        self.load_dataset_config_btn = PrimaryPushButton(FluentIcon.UPDATE,
                                                         self.tr('select folder'))

        self.dataset_hly = QHBoxLayout()
        self.dataset_hly.addWidget(self.dataset_config_led)
        self.dataset_hly.addWidget(self.load_dataset_config_btn)

        self.dataset_vly = QVBoxLayout()
        self.dataset_vly.addWidget(self.dataset_lbl)
        self.dataset_vly.addLayout(self.dataset_hly)

        # epoch
        self.epoch_lbl = BodyLabel(self.tr('epoch: '), self)
        self.epoch_led = LineEdit()
        self.epoch_led.setText("10")

        # batch size
        self.batch_size_lbl = BodyLabel(self.tr('batch size: '), self)
        self.batch_size_led = LineEdit()
        self.batch_size_led.setText("16")

        # learning rate
        self.learning_rate_lbl = BodyLabel(self.tr('learning rate: '), self)
        self.learning_rate_led = LineEdit()
        self.learning_rate_led.setText("0.0025")

        # workers
        self.workers_lbl = BodyLabel(self.tr('workers: '), self)
        self.workers_led = LineEdit()
        self.workers_led.setText("0")

        self.epoch_vly = QVBoxLayout()
        self.batch_size_vly = QVBoxLayout()
        self.learning_rate_vly = QVBoxLayout()
        self.workers_vly = QVBoxLayout()

        self.epoch_vly.addWidget(self.epoch_lbl)
        self.epoch_vly.addWidget(self.epoch_led)

        self.batch_size_vly.addWidget(self.batch_size_lbl)
        self.batch_size_vly.addWidget(self.batch_size_led)

        self.learning_rate_vly.addWidget(self.learning_rate_lbl)
        self.learning_rate_vly.addWidget(self.learning_rate_led)

        self.workers_vly.addWidget(self.workers_lbl)
        self.workers_vly.addWidget(self.workers_led)

        self.hly = QHBoxLayout()
        self.hly.setSpacing(10)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.hly.addLayout(self.epoch_vly)
        self.hly.addLayout(self.batch_size_vly)
        self.hly.addLayout(self.learning_rate_vly)
        self.hly.addLayout(self.workers_vly)

        self.vly = QVBoxLayout()
        self.vly.addLayout(self.dataset_vly)
        self.vly.addLayout(self.hly)
        self.viewLayout.addLayout(self.vly)
        self._connect_signals_and_slots()

        self.train_param = TrainParameter()

    def _connect_signals_and_slots(self):
        self.epoch_led.textChanged.connect(self._on_epoch_changed)
        self.batch_size_led.textChanged.connect(self._on_batch_size_changed)
        self.learning_rate_led.textChanged.connect(self._on_learning_rate_changed)
        self.workers_led.textChanged.connect(self._on_workers_changed)

    @Slot(int)
    def _on_epoch_changed(self, epoch: int):
        self.train_param.epoch = int(epoch)
        self.train_param_changed.emit(self.train_param)

    @Slot(int)
    def _on_batch_size_changed(self, batch_size: int):
        self.train_param.batch_size = int(batch_size)
        self.train_param_changed.emit(self.train_param)

    @Slot(float)
    def _on_learning_rate_changed(self, learning_rate: float):
        self.train_param.learning_rate = float(learning_rate)
        self.train_param_changed.emit(self.train_param)

    @Slot(int)
    def _on_workers_changed(self, workers: int):
        self.train_param.workers = int(workers)
        self.train_param_changed.emit(self.train_param)
