from PySide6.QtCore import Slot, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QCursor
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QListWidgetItem, QListView)
from qfluentwidgets import ComboBox, CheckBox, isDarkTheme, Theme, ListWidget

from settings.config import cfg
from common.utils import *
from .data_convert_thread import LoadDatasetInfo
from .dataset_draw_thread import DatasetDrawThread
from common.image_tip_widget import ImageTip

SMALL = QSize(60, 60)
MEDIUM = QSize(120, 120)
LARGE = QSize(200, 200)

RESOLUTIONS = [SMALL, MEDIUM, LARGE]
DATASET_TYPES = ["train", "val", "test"]


class DatasetDrawWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.cmb_dataset_max_num = ComboBox()
        self.cmb_dataset_max_num.addItems([self.tr("50"), self.tr("100"), self.tr("200"), self.tr("500")])
        self.cmb_dataset_max_num.setCurrentIndex(1)
        self.cmb_dataset_max_num.setMinimumWidth(100)
        self.cmb_dataset_max_num.setMaximumWidth(300)

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
        self.dataset_show_option_hly.addWidget(self.cmb_dataset_max_num)
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
        self.dataset_draw_thread.finished.connect(self._on_draw_image_finished)

        self._set_qss()
        self._connect_signals_and_slots()

        self.dataset_info = LoadDatasetInfo()
        self.max_draw_num = int(self.cmb_dataset_max_num.currentText())
        self.current_resolution = MEDIUM
        self.dataset_type = ""
        self.draw_labels = self.ckb_show_label.isChecked()

    @Slot()
    def _on_draw_image_finished(self):
        self._enable_draw_image_option()

    @Slot(str, QPixmap)
    def _on_draw_image(self, filename: str, pix: QPixmap):
        item = QListWidgetItem()
        item.setIcon(QIcon(pix))
        item.setSizeHint(self.current_resolution)
        item.setToolTip(filename)
        item.setData(Qt.ItemDataRole.UserRole, pix)
        self.lw_image.addItem(item)

    def _connect_signals_and_slots(self):
        cfg.themeChanged.connect(self._on_theme_changed)
        self.cmb_dataset_resolution.currentIndexChanged.connect(self._on_resolution_changed)
        self.cmb_dataset_type.currentIndexChanged.connect(self._on_dateset_type_changed)
        self.ckb_show_label.checkStateChanged.connect(self._on_show_label_status_changed)
        self.cmb_dataset_max_num.currentTextChanged.connect(self._on_max_num_changed)
        self.lw_image.itemDoubleClicked.connect(self._on_item_double_clicked)

    @Slot(QListWidgetItem)
    def _on_item_double_clicked(self, item: QListWidgetItem):
        pix: QPixmap = item.data(Qt.ItemDataRole.UserRole)
        max_screen_side = max(QApplication.primaryScreen().geometry().width(),
                              QApplication.primaryScreen().geometry().height())
        max_image_side = max(pix.width(), pix.height())
        max_side = min(max_image_side, int(max_screen_side * 0.6))
        self.image_tip = ImageTip(pix, QCursor.pos(), max_side)
        self.image_tip.showFlyout()

    @Slot(int)
    def _on_max_num_changed(self, text):
        self.dataset_draw_thread.set_max_draw_nums(int(text))
        self._draw_images()

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
        self._disable_draw_image_option()
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
        self.dataset_draw_thread.set_max_draw_nums(self.max_draw_num)
        self._draw_images()

    def _disable_draw_image_option(self):
        self.cmb_dataset_max_num.setEnabled(False)
        self.cmb_dataset_resolution.setEnabled(False)
        self.cmb_dataset_type.setEnabled(False)
        self.ckb_show_label.setEnabled(False)

    def _enable_draw_image_option(self):
        self.cmb_dataset_max_num.setEnabled(True)
        self.cmb_dataset_resolution.setEnabled(True)
        self.cmb_dataset_type.setEnabled(True)
        self.ckb_show_label.setEnabled(True)

    @Slot(Theme)
    def _on_theme_changed(self, theme):
        self._set_qss()

    def _set_qss(self):
        """ set style sheet """
        if isDarkTheme():
            self.setStyleSheet(f"QScrollArea{{background-color:{DARK_BG}}}")
        else:
            self.setStyleSheet(f"QScrollArea{{background-color:{LIGHT_BG}}}")
