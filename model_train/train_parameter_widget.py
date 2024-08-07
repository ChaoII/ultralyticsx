from pathlib import Path

from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QFileDialog
from qfluentwidgets import HeaderCardWidget, BodyLabel, LineEdit, PrimaryPushButton, FluentIcon, \
    CompactSpinBox, CompactDoubleSpinBox


class TrainParameter:
    dataset_config: str
    epoch: int = 0
    batch_size: int = 0
    learning_rate: float = 0.0
    workers: int = 0


class ModelTrainParamCard(HeaderCardWidget):
    """ Model information card """
    # model name and is use pretrain model
    train_param_changed = Signal(TrainParameter)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.train_param = TrainParameter()

        self.setTitle(self.tr("model training parameter"))

        self.lbl_dataset = BodyLabel(self.tr('dataset config file path: '), self)
        self.led_dataset_config = LineEdit()
        self.led_dataset_config.setPlaceholderText(self.tr("please select a dataset config file"))
        self.btn_load_dataset_config = PrimaryPushButton(FluentIcon.UPDATE,
                                                         self.tr('select folder'))

        self.hly_dataset = QHBoxLayout()
        self.hly_dataset.addWidget(self.led_dataset_config)
        self.hly_dataset.addWidget(self.btn_load_dataset_config)

        self.vly_dataset = QVBoxLayout()
        self.vly_dataset.addWidget(self.lbl_dataset)
        self.vly_dataset.addLayout(self.hly_dataset)

        # epoch
        self.lbl_epoch = BodyLabel(self.tr('epoch: '), self)
        self.sp_epoch = CompactSpinBox()
        self.sp_epoch.setRange(1, 500)
        self.sp_epoch.setValue(10)
        self.train_param.epoch = 10

        # batch size
        self.lbl_batch_size = BodyLabel(self.tr('batch size: '), self)
        self.sp_batch_size = CompactSpinBox()
        self.sp_batch_size.setRange(1, 32)
        self.sp_batch_size.setValue(16)
        self.train_param.batch_size = 16

        # learning rate
        self.lbl_learning_rate = BodyLabel(self.tr('learning rate: '), self)
        self.dsp_learning_rate = CompactDoubleSpinBox()
        self.dsp_learning_rate.setDecimals(6)
        self.dsp_learning_rate.setRange(0, 0.5)
        self.dsp_learning_rate.setValue(0.0025)
        self.train_param.learning_rate = 0.0025

        # workers
        self.lbl_workers = BodyLabel(self.tr('workers: '), self)
        self.sp_workers = CompactSpinBox()
        self.sp_workers.setRange(0, 8)
        self.sp_workers.setValue(0)
        self.train_param.workers = 0

        self.vly_epoch = QVBoxLayout()
        self.vly_batch_size = QVBoxLayout()
        self.vly_learning_rate = QVBoxLayout()
        self.vly_workers = QVBoxLayout()

        self.vly_epoch.addWidget(self.lbl_epoch)
        self.vly_epoch.addWidget(self.sp_epoch)

        self.vly_batch_size.addWidget(self.lbl_batch_size)
        self.vly_batch_size.addWidget(self.sp_batch_size)

        self.vly_learning_rate.addWidget(self.lbl_learning_rate)
        self.vly_learning_rate.addWidget(self.dsp_learning_rate)

        self.vly_workers.addWidget(self.lbl_workers)
        self.vly_workers.addWidget(self.sp_workers)

        self.hly = QHBoxLayout()
        self.hly.setSpacing(10)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.hly.addLayout(self.vly_epoch)
        self.hly.addLayout(self.vly_batch_size)
        self.hly.addLayout(self.vly_learning_rate)
        self.hly.addLayout(self.vly_workers)

        self.vly = QVBoxLayout()
        self.vly.addLayout(self.vly_dataset)
        self.vly.addLayout(self.hly)
        self.viewLayout.addLayout(self.vly)
        self._connect_signals_and_slots()

    def get_epochs(self) -> int:
        return self.sp_epoch.value()

    def _connect_signals_and_slots(self):
        self.sp_epoch.valueChanged.connect(self._on_epoch_changed)
        self.sp_batch_size.valueChanged.connect(self._on_batch_size_changed)
        self.dsp_learning_rate.valueChanged.connect(self._on_learning_rate_changed)
        self.sp_workers.valueChanged.connect(self._on_workers_changed)
        self.btn_load_dataset_config.clicked.connect(self._on_clicked_load_dataset_config)
        self.led_dataset_config.textChanged.connect(self._on_data_config_text_changed)

    @Slot(str)
    def _on_data_config_text_changed(self, file_path):
        self.train_param.dataset_config = file_path
        self.train_param_changed.emit(self.train_param)

    @Slot(int)
    def _on_epoch_changed(self, epoch: int):
        self.train_param.epoch = epoch
        self.train_param_changed.emit(self.train_param)

    @Slot(int)
    def _on_batch_size_changed(self, batch_size: int):
        self.train_param.batch_size = batch_size
        self.train_param_changed.emit(self.train_param)

    @Slot(float)
    def _on_learning_rate_changed(self, learning_rate: float):
        self.train_param.learning_rate = learning_rate
        self.train_param_changed.emit(self.train_param)

    @Slot(int)
    def _on_workers_changed(self, workers: int):
        self.train_param.workers = workers
        self.train_param_changed.emit(self.train_param)

    @Slot()
    def _on_clicked_load_dataset_config(self):
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("info"), self.tr("select a dataset config file"), "",
                                                  "All Files (*);;yaml (yaml,yml)")
        filename_normal = Path(filename).resolve().as_posix()
        self.led_dataset_config.setText(filename_normal)
