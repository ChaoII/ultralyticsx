import os
from enum import Enum
from pathlib import Path

import qfluentwidgets
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QPushButton, QGroupBox, QGridLayout,
                               QLabel, QLineEdit, QFileDialog, QFormLayout, QSplitter, QScrollArea, QFrame,
                               QListWidgetItem, QListView)

from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QFont, QBrush, QFontMetrics

from qfluentwidgets import HeaderCardWidget, BodyLabel, LineEdit, PrimaryPushButton, FluentIcon, ImageLabel, TextEdit, \
    FlowLayout, ComboBox, CheckBox, SingleDirectionScrollArea, SmoothScrollArea, isDarkTheme, ScrollArea, setTheme, \
    Theme, ExpandLayout, SimpleCardWidget, CaptionLabel, ListWidget

from PySide6.QtCore import Slot, Qt, QEasingCurve, QAbstractItemModel, QSize, Signal, QRect, QThread
from .utils import DataConvertThread, LoadDatasetInfo
from settings.config import cfg
from utils.utils import *
from .DatasetDrawThread import DatasetDrawThread

SMALL = QSize(60, 60)
MEDIUM = QSize(120, 120)
LARGE = QSize(200, 200)

RESOLUTIONS = [SMALL, MEDIUM, LARGE]
DATASET_TYPES = ["train", "val", "test"]


class DatasetDrawWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.cmb_dataset_type = ComboBox()
        self.cmb_dataset_type.addItems([self.tr("train"), self.tr("val"), self.tr("test")])
        self.cmb_dataset_type.setCurrentIndex(0)
        self.cmb_dataset_type.setMinimumWidth(100)
        self.cmb_dataset_type.setMaximumWidth(300)

        self.cmb_dataset_resolution = ComboBox()
        self.cmb_dataset_resolution.addItems([self.tr("small"), self.tr("medium"), self.tr("large")])
        self.cmb_dataset_resolution.setCurrentIndex(1)
        self.cmb_dataset_resolution.setMinimumWidth(100)
        self.cmb_dataset_resolution.setMaximumWidth(300)

        self.ckb_show_label = CheckBox()
        self.ckb_show_label.setText(self.tr("show label"))
        self.ckb_show_label.setChecked(True)

        self.dataset_show_option_hly = QHBoxLayout()
        self.dataset_show_option_hly.addStretch(1)
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_resolution)
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_type)
        self.dataset_show_option_hly.addWidget(self.ckb_show_label)

        self.lw_image = ListWidget()
        self.lw_image.setFlow(QListView.Flow.LeftToRight)
        # 必须加
        self.lw_image.setResizeMode(QListView.ResizeMode.Adjust)
        # 禁用横向滚动条
        self.lw_image.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.lw_image.setSpacing(0)
        self.lw_image.setViewMode(QListView.ViewMode.IconMode)
        self.lw_image.setIconSize(QSize(120, 120))

        self.vly = QVBoxLayout(self)
        self.vly.addLayout(self.dataset_show_option_hly)
        self.vly.addWidget(self.lw_image)

        self.dataset_draw_thread = DatasetDrawThread()
        self.dataset_draw_thread.draw_labels_finished.connect(self._on_draw_image)

        self._set_qss()
        self._connect_signals_and_slots()

        self.dataset_info = LoadDatasetInfo()
        self.draw_nums = 50
        self.current_resolution = MEDIUM
        self.dataset_type = ""
        self.draw_labels = False

    @Slot(QPixmap)
    def _on_draw_image(self, pix: QPixmap):
        item = QListWidgetItem()
        item.setIcon(QIcon(pix))
        item.setSizeHint(self.current_resolution)
        self.lw_image.addItem(item)

    def _connect_signals_and_slots(self):
        cfg.themeChanged.connect(self._on_theme_changed)
        self.cmb_dataset_resolution.currentIndexChanged.connect(self._on_resolution_changed)
        self.cmb_dataset_type.currentIndexChanged.connect(self._on_dateset_type_changed)
        self.ckb_show_label.checkStateChanged.connect(self._on_show_label_status_changed)

    @Slot(int)
    def _on_resolution_changed(self, index):
        self.current_resolution = RESOLUTIONS[index]
        self.lw_image.setIconSize(self.current_resolution)
        self._draw_images()

    @Slot(int)
    def _on_dateset_type_changed(self, index):
        self.dataset_type = DATASET_TYPES[index]
        image_path = Path(self.dataset_info.dataset_dir) / "images" / self.dataset_type
        annotation_path = Path(self.dataset_info.dataset_dir) / "labels" / self.dataset_type
        if not image_path.exists() or not annotation_path.exists():
            return
        self.dataset_draw_thread.set_dataset_path(image_path, annotation_path)
        self._draw_images()

    @Slot(Qt.CheckState)
    def _on_show_label_status_changed(self, status):
        self.draw_labels = Qt.CheckState.Checked == status
        self.dataset_draw_thread.set_draw_labels_status(self.draw_labels)
        self._draw_images()

    def _draw_images(self):
        self.lw_image.clear()
        self.dataset_draw_thread.start()

    def draw_images(self, dataset_info: LoadDatasetInfo):
        self.dataset_info = dataset_info
        image_path = Path(dataset_info.dataset_dir) / "images" / "train"
        annotation_path = Path(dataset_info.dataset_dir) / "labels" / "train"
        if not image_path.exists() or not annotation_path.exists():
            return
        self.dataset_draw_thread.set_dataset_path(image_path, annotation_path)
        self.dataset_draw_thread.set_draw_labels_status(self.draw_labels)
        self.dataset_draw_thread.set_labels_map(dataset_info.labels)
        self._draw_images()

    @Slot(Theme)
    def _on_theme_changed(self, theme):
        self._set_qss()

    def _set_qss(self):
        """ set style sheet """
        if isDarkTheme():
            self.setStyleSheet(f"QScrollArea{{background-color:{DARK_BG}}}")
        else:
            self.setStyleSheet(f"QScrollArea{{background-color:{LIGHT_BG}}}")


class SelectDatasetCard(HeaderCardWidget):
    """ Model information card """
    dataset_file_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("select dataset"))
        self.lbl_dataset = BodyLabel(self.tr('dataset file: '), self)
        self.led_dataset = LineEdit()
        self.led_dataset.setPlaceholderText(self.tr("please select a dataset file for zip"))
        self.btn_load_dataset = PrimaryPushButton(FluentIcon.UPDATE,
                                                  self.tr('select folder'))

        self.hly_dataset = QHBoxLayout(self)
        self.hly_dataset.addWidget(self.lbl_dataset)
        self.hly_dataset.addWidget(self.led_dataset)
        self.hly_dataset.addWidget(self.btn_load_dataset)

        self.viewLayout.addLayout(self.hly_dataset)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_load_dataset.clicked.connect(self.open_file)

    @Slot()
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, self.tr("open dataset file"), "",
                                                   "All Files (*);; Zip File(*.zip)")
        normalize_file_path = Path(file_name).resolve().as_posix()
        self.led_dataset.setText(normalize_file_path)
        self.dataset_file_changed.emit(normalize_file_path)


class DataConvertWidget(QWidget):
    def __init__(self, parent=None):
        super(DataConvertWidget, self).__init__(parent=parent)
        self.setObjectName("dataset_config")

        self.select_card = SelectDatasetCard(self)
        self.btn_data_valid = PrimaryPushButton(FluentIcon.UPDATE, self.tr('data valid'))

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.dataset_info_widget = QWidget()
        self.plot_dataset_info_widget = QWidget()

        fly_dataset_info = QFormLayout()
        fly_dataset_info.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_train_image_num = BodyLabel("training images: ", self)
        self.le_train_image_num = LineEdit()

        self.lbl_train_obj_num = BodyLabel("training object: ", self)
        self.le_train_obj_num = LineEdit()

        self.lbl_val_image_num = BodyLabel("valid images: ", self)
        self.le_val_image_num = LineEdit()

        self.lbl_val_obj_num = BodyLabel("valid object: ", self)
        self.le_val_obj_num = LineEdit()

        self.lbl_test_image_num = BodyLabel("test images: ", self)
        self.le_test_image_num = LineEdit()

        self.lbl_test_obj_num = BodyLabel("test objects: ", self)
        self.le_test_obj_num = LineEdit()

        self.lbl_dataset_config_path = BodyLabel("dataset config path: ", self)
        self.le_dataset_config_path = LineEdit()

        self.lbl_dataset_labels = BodyLabel("dataset labels: ", self)
        self.ted_dataset_labels = TextEdit()

        fly_dataset_info.addRow(self.lbl_train_image_num, self.le_train_image_num)
        fly_dataset_info.addRow(self.lbl_train_obj_num, self.le_train_obj_num)
        fly_dataset_info.addRow(self.lbl_val_image_num, self.le_val_image_num)
        fly_dataset_info.addRow(self.lbl_val_obj_num, self.le_val_obj_num)
        fly_dataset_info.addRow(self.lbl_test_image_num, self.le_test_image_num)
        fly_dataset_info.addRow(self.lbl_test_obj_num, self.le_test_obj_num)
        fly_dataset_info.addRow(self.lbl_dataset_config_path, self.le_dataset_config_path)
        fly_dataset_info.addRow(self.lbl_dataset_labels, self.ted_dataset_labels)

        self.dataset_info_widget.setLayout(fly_dataset_info)
        self.dataset_draw_widget = DatasetDrawWidget()
        self.splitter.addWidget(self.dataset_info_widget)
        self.splitter.addWidget(self.dataset_draw_widget)

        v_layout = QVBoxLayout(self)

        v_layout.addWidget(self.select_card)
        v_layout.addWidget(self.btn_data_valid)
        v_layout.addWidget(self.splitter)

        # v_layout.addWidget(gb_dataset_config_path)
        # v_layout.addWidget(gb_dataset_labels)

        self.data_convert_thread = DataConvertThread()
        self._connect_signals_and_slot()

    def _connect_signals_and_slot(self):
        self.btn_data_valid.clicked.connect(self.data_valid)
        self.select_card.dataset_file_changed.connect(self._on_update_dataset)
        self.data_convert_thread.dataset_resolve_finished.connect(self._on_dataset_resolve_finished)

    @Slot(str)
    def _on_update_dataset(self, dataset_path: str):
        self.data_convert_thread.set_dataset_path(dataset_path)

    @Slot(LoadDatasetInfo)
    def _on_dataset_resolve_finished(self, dataset_info: LoadDatasetInfo):
        self.le_train_image_num.setText(str(dataset_info.train_image_num))
        self.le_train_obj_num.setText(str(dataset_info.train_obj_num))
        self.le_val_image_num.setText(str(dataset_info.val_image_num))
        self.le_val_obj_num.setText(str(dataset_info.val_obj_num))
        self.le_test_image_num.setText(str(dataset_info.test_image_num))
        self.le_test_obj_num.setText(str(dataset_info.test_obj_num))
        self.le_dataset_config_path.setText(dataset_info.dst_yaml_path)
        self.ted_dataset_labels.append("\n".join(f"{k}: {v}" for k, v in dataset_info.labels.items()))
        self.dataset_draw_widget.draw_images(dataset_info)

    @Slot()
    def data_valid(self):
        self.data_convert_thread.start()
