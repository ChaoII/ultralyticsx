import enum

import pandas as pd
from PySide6.QtCore import Slot, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QListView, QListWidgetItem, QApplication
from qfluentwidgets import SimpleCardWidget, ComboBox, CheckBox, ListWidget

from common.component.image_tip_widget import ImageTip
from .dataset_draw_thread_base import DatasetDrawThreadBase
from ...types import DatasetType


class ImageItemSize(enum.Enum):
    SMALL = QSize(60, 60)
    MEDIUM = QSize(120, 120)
    LARGE = QSize(200, 200)


class DatasetDrawWidgetBase(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.cmb_dataset_max_num = ComboBox()
        self.cmb_dataset_max_num.addItems(["50", "100", "200", "500"])
        self.cmb_dataset_max_num.setCurrentIndex(1)
        self.cmb_dataset_max_num.setMinimumWidth(100)
        self.cmb_dataset_max_num.setMaximumWidth(300)

        self.cmb_dataset_resolution = ComboBox()
        self.cmb_dataset_resolution.addItems([self.tr("small"), self.tr("medium"), self.tr("large")])
        self.cmb_dataset_resolution.setItemData(0, ImageItemSize.SMALL)
        self.cmb_dataset_resolution.setItemData(1, ImageItemSize.MEDIUM)
        self.cmb_dataset_resolution.setItemData(2, ImageItemSize.LARGE)
        self.cmb_dataset_resolution.setCurrentIndex(1)
        self.cmb_dataset_resolution.setMinimumWidth(100)
        self.cmb_dataset_resolution.setMaximumWidth(300)

        self.cmb_dataset_type = ComboBox()
        self.cmb_dataset_type.addItems([self.tr("all"), self.tr("train"), self.tr("val"), self.tr("test")])
        self.cmb_dataset_type.setItemData(0, DatasetType.ALL)
        self.cmb_dataset_type.setItemData(1, DatasetType.TRAIN)
        self.cmb_dataset_type.setItemData(2, DatasetType.VAL)
        self.cmb_dataset_type.setItemData(3, DatasetType.TEST)
        self.cmb_dataset_type.setCurrentIndex(1)
        self.cmb_dataset_type.setMinimumWidth(100)
        self.cmb_dataset_type.setMaximumWidth(300)

        self.cmb_dataset_label = ComboBox()
        self.cmb_dataset_label.setCurrentIndex(0)
        self.cmb_dataset_label.setMinimumWidth(120)
        self.cmb_dataset_label.setMaximumWidth(300)

        self.ckb_show_label = CheckBox()
        self.ckb_show_label.setText(self.tr("show label"))
        self.ckb_show_label.setChecked(True)

        self.dataset_show_option_hly = QHBoxLayout()
        self.dataset_show_option_hly.addStretch(1)
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_max_num)
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_resolution)
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_type)
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_label)
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

        self.dataset_draw_thread: DatasetDrawThreadBase | None = None

        self.vly = QVBoxLayout(self)
        self.vly.addLayout(self.dataset_show_option_hly)
        self.vly.addWidget(self.lw_image)

        self.set_dataset_draw_thread()

        self._connect_signals_and_slots()

        self._dataset_df: pd.DataFrame = pd.DataFrame()

        self.max_draw_num = int(self.cmb_dataset_max_num.currentText())
        self.image_resolution = ImageItemSize.MEDIUM
        self.dataset_type = DatasetType.TRAIN
        self.dataset_label = "all"
        self.draw_labels = self.ckb_show_label.isChecked()

    def get_current_condition_dataset(self) -> pd.DataFrame:
        raise NotImplementedError

    def set_dataset_draw_thread(self):
        raise NotImplementedError

    def init_dataset_labels(self, dataset_df: pd.DataFrame):
        raise NotImplementedError

    def update_dataset(self, dataset_df: pd.DataFrame):
        self._dataset_df = dataset_df
        self.init_dataset_labels(dataset_df)
        self._draw_images()

    #
    def _connect_signals_and_slots(self):
        self.cmb_dataset_resolution.currentIndexChanged.connect(self._on_resolution_changed)
        self.cmb_dataset_type.currentIndexChanged.connect(self._on_dateset_type_changed)
        self.ckb_show_label.checkStateChanged.connect(self._on_show_label_status_changed)
        self.cmb_dataset_max_num.currentTextChanged.connect(self._on_max_num_changed)
        self.cmb_dataset_label.currentTextChanged.connect(self._on_dataset_label_changed)
        self.lw_image.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.dataset_draw_thread.draw_one_image.connect(self._on_draw_image)
        self.dataset_draw_thread.finished.connect(self._on_draw_image_finished)

    @Slot()
    def _on_draw_image_finished(self):
        self._enable_draw_image_option()

    @Slot(QListWidgetItem)
    def _on_item_double_clicked(self, item: QListWidgetItem):
        pix: QPixmap = item.data(Qt.ItemDataRole.UserRole)
        self.image_tip = ImageTip(pix, QCursor.pos())
        self.image_tip.showFlyout()

    @Slot(str)
    def _on_max_num_changed(self, text):
        self.max_draw_num = int(text)
        self._draw_images()

    @Slot(str)
    def _on_dataset_label_changed(self, text):
        self.dataset_label = text
        self._draw_images()

    @Slot(str, QPixmap)
    def _on_draw_image(self, filename: str, pix: QPixmap):
        item = QListWidgetItem()
        item.setIcon(QIcon(pix))
        item.setText(filename)
        item.setSizeHint(self.image_resolution.value)
        item.setToolTip(filename)
        item.setData(Qt.ItemDataRole.UserRole, pix)
        self.lw_image.addItem(item)

    @Slot(int)
    def _on_resolution_changed(self, index):
        self.image_resolution = self.cmb_dataset_resolution.itemData(index)
        self.lw_image.setIconSize(self.image_resolution.value)
        self._draw_images()

    @Slot(int)
    def _on_dateset_type_changed(self, index):
        self.dataset_type = self.cmb_dataset_type.itemData(index)
        self._draw_images()

    @Slot(Qt.CheckState)
    def _on_show_label_status_changed(self, status):
        self.draw_labels = Qt.CheckState.Checked == status
        self._draw_images()

    def _draw_images(self):
        self._disable_draw_image_option()
        self.lw_image.clear()
        image_paths = self.get_current_condition_dataset()
        self.dataset_draw_thread.set_max_draw_nums(self.max_draw_num)
        self.dataset_draw_thread.set_dataset_path(image_paths)
        self.dataset_draw_thread.set_draw_labels_status(self.draw_labels)
        self.dataset_draw_thread.start()

    def _disable_draw_image_option(self):
        self.cmb_dataset_max_num.setEnabled(False)
        self.cmb_dataset_resolution.setEnabled(False)
        self.cmb_dataset_type.setEnabled(False)
        self.cmb_dataset_label.setEnabled(False)
        self.ckb_show_label.setEnabled(False)

    def _enable_draw_image_option(self):
        self.cmb_dataset_max_num.setEnabled(True)
        self.cmb_dataset_resolution.setEnabled(True)
        self.cmb_dataset_type.setEnabled(True)
        self.cmb_dataset_label.setEnabled(True)
        self.ckb_show_label.setEnabled(True)
