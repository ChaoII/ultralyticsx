from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QPushButton, QGroupBox, QGridLayout,
                               QLineEdit, QTextEdit, QProgressBar, QComboBox, QCheckBox)
from options import *
from PySide6.QtCore import Slot, Signal, Qt, QThread, QCoreApplication
from loguru import logger
import threading
from trainer import ModelTrainThread, log_format_info, log_format_error, log_format_warning


class ModelTrainWidget(QWidget):
    start_train_model_signal = Signal(str, int, int, float, int)
    stop_train_model_signal = Signal()

    def __init__(self):
        super(ModelTrainWidget, self).__init__()
        # setup ui
        h_layout = QHBoxLayout()
        self.cmb_model_type = QComboBox()
        self.cmb_model_name = QComboBox()
        self.ckb_use_pretrain = QCheckBox("是否使用预训练模型")

        h_layout.addWidget(self.cmb_model_type)
        h_layout.addWidget(self.cmb_model_name)
        h_layout.addWidget(self.ckb_use_pretrain)

        gly = QGridLayout()
        self.le_epoch = QLineEdit("10")
        self.le_batch = QLineEdit("16")
        self.le_learning_rate = QLineEdit("0.0025")
        self.le_workers = QLineEdit("0")

        gb_epoch = QGroupBox("训练轮数(epoch)")
        vly_train_image_num = QVBoxLayout()
        vly_train_image_num.addWidget(self.le_epoch)
        gb_epoch.setLayout(vly_train_image_num)

        gb_batch_size = QGroupBox("批次大小(batch size)")
        vly_train_obj_num = QVBoxLayout()
        vly_train_obj_num.addWidget(self.le_batch)
        gb_batch_size.setLayout(vly_train_obj_num)

        gb_learning_rate = QGroupBox("学习率")
        vly_val_image_num = QVBoxLayout()
        vly_val_image_num.addWidget(self.le_learning_rate)
        gb_learning_rate.setLayout(vly_val_image_num)

        gb_workers = QGroupBox("dataloader进程数")
        vly_val_obj_num = QVBoxLayout()
        vly_val_obj_num.addWidget(self.le_workers)
        gb_workers.setLayout(vly_val_obj_num)

        gly.addWidget(gb_epoch, 0, 0)
        gly.addWidget(gb_batch_size, 0, 1)
        gly.addWidget(gb_learning_rate, 0, 2)
        gly.addWidget(gb_workers, 0, 3)

        gly_btn = QGridLayout()
        self.btn_start_train = QPushButton("开始训练")
        self.btn_stop_train = QPushButton("结束训练")

        gly_btn.addWidget(self.btn_start_train, 0, 0)
        gly_btn.addWidget(self.btn_stop_train, 0, 1)

        self.psb_train = QProgressBar()
        self.psb_train.setValue(0)
        self.psb_train.setMaximum(int(self.le_epoch.text()))
        self.psb_train.setFormat("%v/%m")  # 设置显示的格式为“当前值/最大值”

        self.ted_train_log = QTextEdit()
        gb_train_log = QGroupBox("训练日志")
        vly_train_log = QVBoxLayout()
        vly_train_log.addWidget(self.ted_train_log)
        gb_train_log.setLayout(vly_train_log)
        gb_train_log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        v_layout = QVBoxLayout(self)
        v_layout.addLayout(h_layout)
        v_layout.addLayout(gly)
        v_layout.addLayout(gly_btn)
        v_layout.addWidget(self.psb_train)
        v_layout.addWidget(gb_train_log)

        self.btn_stop_train.setEnabled(False)

        self.cmb_model_type.currentTextChanged.connect(self._set_model_name)
        self.cmb_model_name.currentTextChanged.connect(self.on_model_name_changed)
        self.ckb_use_pretrain.checkStateChanged.connect(self.on_use_pretrain_model_status_changed)
        self.le_epoch.textChanged.connect(lambda x: self.psb_train.setMaximum(int(x)))

        self.btn_start_train.clicked.connect(self.start_train)
        self.btn_stop_train.clicked.connect(self.stop_train)

        # define
        self.model_thread = None
        self.current_model_name = ""
        self.use_pretrain = False
        self._train_finished = True
        self._resume = False
        self._last_model = ""
        self._init_model_type_and_name_cmb()

    def _init_model_type_and_name_cmb(self):
        # 初始化模型类型列表
        for model_type in model_type_option:
            self.cmb_model_type.addItem(model_type)
        # 初始化模型名称
        model_names = type_model_mapping.get(model_type_option[0], [])
        for model_name in model_names:
            self.cmb_model_name.addItem(model_name)
        # 初始化模型
        self.current_model_name = self.cmb_model_name.currentText()

    def _initial_model(self,
                       current_model_name: str,
                       use_pretrain: bool,
                       data_config: str,
                       epochs: int,
                       batch_size: int,
                       learning_rate: float,
                       workers: int,
                       resume: bool):
        logger.info(f"main thread, thread id is: {threading.get_ident()}")
        self.model_thread = ModelTrainThread(current_model_name,
                                             use_pretrain,
                                             data_config,
                                             epochs,
                                             batch_size,
                                             learning_rate,
                                             workers,
                                             resume)
        self._train_finished = False
        self.model_thread.train_epoch_start_signal.connect(self.on_handle_epoch_start)
        self.model_thread.train_batch_end_signal.connect(self.on_handle_batch_end)
        self.model_thread.train_epoch_end_signal.connect(self.on_handle_epoch_end)
        self.model_thread.fit_epoch_end_signal.connect(self.on_handle_fit_epoch_end)
        self.model_thread.train_end_signal.connect(self.on_handle_train_end)

        self.stop_train_model_signal.connect(self.model_thread.stop_train)

    @Slot(str)
    def _set_model_name(self, model_type: str):
        self.cmb_model_name.clear()
        model_names = type_model_mapping.get(model_type, [])
        for model_name in model_names:
            self.cmb_model_name.addItem(model_name)

    def _turn_widget_enable_status(self):
        self.cmb_model_type.setEnabled(not self.cmb_model_type.isEnabled())
        self.cmb_model_name.setEnabled(not self.cmb_model_name.isEnabled())
        self.ckb_use_pretrain.setEnabled(not self.ckb_use_pretrain.isEnabled())

        self.le_epoch.setEnabled(not self.le_epoch.isEnabled())
        self.le_batch.setEnabled(not self.le_batch.isEnabled())
        self.le_learning_rate.setEnabled(not self.le_learning_rate.isEnabled())
        self.le_workers.setEnabled(not self.le_workers.isEnabled())

        self.btn_start_train.setEnabled(not self.btn_start_train.isEnabled())
        self.btn_stop_train.setEnabled(not self.btn_stop_train.isEnabled())

    @Slot()
    def start_train(self):
        self.ted_train_log.append(log_format_info(f"模型{self.current_model_name}开始训练"))
        if not self._train_finished:
            self._resume = True
        if self._last_model:
            current_model_name = self._last_model
        else:
            current_model_name = self.current_model_name
            self._resume = False

        self._initial_model(current_model_name, self.use_pretrain,
                            "C:/Users/AC/.gradio/projects/20240723175626306516/coco_cpy.yaml",
                            int(self.le_epoch.text()), int(self.le_batch.text()),
                            float(self.le_learning_rate.text()),
                            int(self.le_workers.text()), self._resume)
        self._turn_widget_enable_status()
        self.model_thread.start()

    @Slot(str)
    def on_model_name_changed(self, model_name: str):
        self.current_model_name = model_name

    @Slot(Qt.CheckState)
    def on_use_pretrain_model_status_changed(self, status: Qt.CheckState):
        self.use_pretrain = Qt.CheckState.Checked == status

    @Slot()
    def stop_train(self):
        self.stop_train_model_signal.emit()
        self.model_thread.quit()
        self.model_thread.wait()
        self._turn_widget_enable_status()
        # 立即刷新界面
        QCoreApplication.processEvents()
        self.ted_train_log.append(log_format_info("执行手动停止训练指令，等待训练结束"))

    @Slot(str)
    def on_handle_epoch_start(self, split: str):
        self.ted_train_log.append(split)

    @Slot(str)
    def on_handle_batch_end(self, metrics: str):
        self.ted_train_log.append(metrics)

    @Slot(int, str)
    def on_handle_epoch_end(self, epoch: int, last_model: str):
        self._last_model = last_model
        self.psb_train.setValue(epoch)

    @Slot(str)
    def on_handle_fit_epoch_end(self, format_metrics: str):
        self.ted_train_log.append(format_metrics)

    @Slot(int)
    def on_handle_train_end(self, cur_epoch: int):
        self._turn_widget_enable_status()
        if cur_epoch == int(self.le_epoch.text()):
            self._train_finished = True
            self.ted_train_log.append(log_format_info("训练完成"))
        self.ted_train_log.append(log_format_info(f"训练被手动终止没当前已训练轮次，{cur_epoch}"))
