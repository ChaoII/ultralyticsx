import qfluentwidgets
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QPushButton, QGroupBox, QGridLayout,
                               QLabel, QLineEdit, QFileDialog, QFormLayout, QSplitter, QScrollArea, QFrame,
                               QListWidgetItem, QListView)

from PySide6.QtGui import QIcon

from qfluentwidgets import HeaderCardWidget, BodyLabel, LineEdit, PrimaryPushButton, FluentIcon, ImageLabel, TextEdit, \
    FlowLayout, ComboBox, CheckBox, SingleDirectionScrollArea, SmoothScrollArea, isDarkTheme, ScrollArea, setTheme, \
    Theme, ExpandLayout, SimpleCardWidget, CaptionLabel, ListWidget

from PySide6.QtCore import Slot, Qt, QEasingCurve, QAbstractItemModel, QSize
from .utils import convert
from settings.config import cfg
from utils.utils import *


class DatasetDraw(QWidget):

    def __init__(self):
        super().__init__()

        self.cmb_dataset_type = ComboBox()
        self.cmb_dataset_type.addItems([self.tr("train"), self.tr("val"), self.tr("test")])
        self.cmb_dataset_type.setCurrentIndex(0)
        self.cmb_dataset_type.setMinimumWidth(100)
        self.cmb_dataset_type.setMaximumWidth(300)

        self.cmb_dataset_resolution = ComboBox()
        self.cmb_dataset_resolution.addItems([self.tr("big"), self.tr("medium"), self.tr("small")])
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

        listWidget = ListWidget()
        listWidget.setFlow(QListView.Flow.LeftToRight)
        # 必须加
        listWidget.setResizeMode(QListView.ResizeMode.Adjust)
        listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        listWidget.setSpacing(0)
        listWidget.setViewMode(QListView.ViewMode.IconMode)
        listWidget.setIconSize(QSize(120, 120))

        for i in range(50):
            item = QListWidgetItem()
            item.setIcon(QIcon(':/qfluentwidgets/images/logo.png'))
            item.setSizeHint(QSize(120, 120))
            listWidget.addItem(item)

        self.vly = QVBoxLayout(self)
        self.vly.addLayout(self.dataset_show_option_hly)
        self.vly.addWidget(listWidget)

        # self.resize(100, 300)
        self._set_qss()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        cfg.themeChanged.connect(self._on_theme_changed)

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("select dataset"))
        self.lbl_dataset = BodyLabel(self.tr('dataset file: '), self)
        self.led_dataset_config = LineEdit()
        self.led_dataset_config.setPlaceholderText(self.tr("please select a dataset file for zip"))
        self.btn_load_dataset_config = PrimaryPushButton(FluentIcon.UPDATE,
                                                         self.tr('select folder'))

        self.hly_dataset = QHBoxLayout(self)
        self.hly_dataset.addWidget(self.lbl_dataset)
        self.hly_dataset.addWidget(self.led_dataset_config)
        self.hly_dataset.addWidget(self.btn_load_dataset_config)

        self.viewLayout.addLayout(self.hly_dataset)

    def _connect_signals_and_slots(self):
        self.btn_load_dataset_config.clicked.connect()

    @Slot()
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开数据集文件目录", "", "All Files (*);;")
        self.led_dataset_config.setText(file_name)


class DataConvertWidget(QWidget):
    def __init__(self, parent=None):
        super(DataConvertWidget, self).__init__(parent=parent)
        self.setObjectName("dataset_config")

        h_layout = QHBoxLayout()
        self.select_card = SelectDatasetCard(self)
        self.btn_data_valid = PrimaryPushButton(FluentIcon.UPDATE,
                                                self.tr('data valid'))

        self.spliter = QSplitter(Qt.Orientation.Horizontal, self)
        self.spliter.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.dataset_info_widget = QWidget()
        self.plot_dataset_info_widget = QWidget()

        fly_dataset_info = QFormLayout()
        self.lbl_train_image_num = BodyLabel("训练集图片数量", self)
        self.le_train_image_num = LineEdit()

        self.lbl_train_obj_num = BodyLabel("训练集对象数量", self)
        self.le_train_obj_num = LineEdit()

        self.lbl_val_image_num = BodyLabel("验证集图片数量", self)
        self.le_val_image_num = LineEdit()

        self.lbl_val_obj_num = BodyLabel("验证集对象数量", self)
        self.le_val_obj_num = LineEdit()

        self.lbl_test_image_num = BodyLabel("测试集图片数量", self)
        self.le_test_image_num = LineEdit()

        self.lbl_test_obj_num = BodyLabel("测试集对象数量", self)
        self.le_test_obj_num = LineEdit()

        self.lbl_dataset_config_path = BodyLabel("测试集对象数量", self)
        self.le_dataset_config_path = LineEdit()

        self.lbl_dataset_labels = BodyLabel("数据集标签", self)
        self.ted_dataset_labels = TextEdit()

        fly_dataset_info.addRow(self.lbl_train_image_num, self.le_train_image_num)
        fly_dataset_info.addRow(self.lbl_val_image_num, self.le_val_image_num)
        fly_dataset_info.addRow(self.lbl_test_image_num, self.le_test_image_num)
        fly_dataset_info.addRow(self.lbl_train_obj_num, self.le_train_obj_num)
        fly_dataset_info.addRow(self.lbl_val_obj_num, self.le_val_obj_num)
        fly_dataset_info.addRow(self.lbl_test_obj_num, self.le_test_obj_num)
        fly_dataset_info.addRow(self.lbl_dataset_config_path, self.le_dataset_config_path)
        fly_dataset_info.addRow(self.lbl_dataset_labels, self.ted_dataset_labels)

        self.dataset_info_widget.setLayout(fly_dataset_info)
        self.spliter.addWidget(self.dataset_info_widget)
        self.spliter.addWidget(DatasetDraw())
        # h_layout.addWidget(Demo())
        # h_layout.addWidget(ImageLabel("vis_result.jpg", self))

        # gb_dataset_labels.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        v_layout = QVBoxLayout(self)

        v_layout.addWidget(self.select_card)
        v_layout.addWidget(self.btn_data_valid)
        v_layout.addWidget(self.spliter)

        # v_layout.addWidget(gb_dataset_config_path)
        # v_layout.addWidget(gb_dataset_labels)

        self.btn_data_valid.clicked.connect(self.data_valid)

    @Slot()
    def data_valid(self):
        (dataset_dir, train_image_num, train_obj_num, val_image_num, val_obj_num,
         test_image_num, test_obj_num, labels, dst_yaml_path) = convert(self.led_file_path.text())
        self.lbl_train_image_num.setText(str(train_image_num))
        self.lbl_train_obj_num.setText(str(train_obj_num))
        self.lbl_val_image_num.setText(str(val_image_num))
        self.lbl_val_obj_num.setText(str(val_obj_num))
        self.lbl_test_image_num.setText(str(test_image_num))
        self.lbl_test_obj_num.setText(str(test_obj_num))
        self.led_dataset_config_path.setText(dst_yaml_path)
        self.ted_dataset_labels.setText(str(labels))
