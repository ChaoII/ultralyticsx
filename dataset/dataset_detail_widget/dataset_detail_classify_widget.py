import enum
import time
from pathlib import Path
import pandas as pd
from PySide6.QtCore import Slot, Qt, QSize, QThread, Signal, QRect
from PySide6.QtGui import QIcon, QPixmap, QCursor, QPainter, QFont, QFontMetrics, QPen, QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QListView, QListWidgetItem, QApplication
from qfluentwidgets import SimpleCardWidget, ComboBox, CheckBox, ListWidget

from common.db_helper import db_session
from common.utils import generate_color_map, invert_color
from dataset.dataset_checker.classify.split_dataset import split_dataset, load_split_dataset
from dataset.dataset_detail_widget.label_table_Widget import LabelTableWidget, SplitLabelInfo
from dataset.types import DatasetInfo, DatasetType, DatasetStatus
from dataset_process.image_tip_widget import ImageTip
from models.models import Dataset


class ImageItemSize(enum.Enum):
    SMALL = QSize(60, 60)
    MEDIUM = QSize(120, 120)
    LARGE = QSize(200, 200)


class ClassifyDatasetLabelsWidget(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(500)
        self.tb_label_info = LabelTableWidget()
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.addWidget(self.tb_label_info)

    def update_table(self, split_rates: list, dataset_split_num_info: list[SplitLabelInfo]):
        self.tb_label_info.set_split_rates(split_rates)
        self.tb_label_info.set_data(dataset_split_num_info)


class DatasetDrawThread(QThread):
    draw_one_image = Signal(str, QPixmap)

    def __init__(self):
        super().__init__()
        self.max_draw_num = 50
        self.draw_labels = False
        self.color_list = []
        self.labels = []
        self.image_paths: pd.DataFrame = pd.DataFrame()

    def set_dataset_path(self, dataset_paths: list[Path]):
        self.image_paths = dataset_paths

    def set_dataset_label(self, labels):
        self.labels = list(labels)
        self.color_list = generate_color_map(len(labels))

    def set_draw_labels_status(self, status: bool):
        self.draw_labels = status

    def set_max_draw_nums(self, max_draw_num: int):
        self.max_draw_num = max_draw_num

    def run(self):
        for i, (index, row) in enumerate(self.image_paths.iterrows()):
            if i >= self.max_draw_num:
                break
            pix = QPixmap(row["image_path"])
            if self.draw_labels:
                label = row["label"]
                # 绘制矩形
                painter = QPainter(pix)
                line_width = min(pix.width(), pix.height()) // 50
                # 设置填充色
                color = self.color_list[self.labels.index(label)]
                inv_color = invert_color(color)
                color.setAlpha(100)
                # 设置边框颜色
                painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
                # 获取字体大小
                font_size = min(pix.width(), pix.height()) // 10  # 假设文字大小是窗口大小的10%
                font = QFont("Microsoft YaHei UI")
                font.setPixelSize(font_size)
                fm = QFontMetrics(font)

                # 文字填充色
                painter.setBrush(color)
                new_rect = QRect(5, 5, fm.boundingRect(label).width() + line_width, fm.height())
                painter.drawRect(new_rect)
                painter.setFont(font)
                painter.setPen(QPen(inv_color))
                painter.drawText(new_rect, label)
                painter.end()
            time.sleep(0.01)
            self.draw_one_image.emit(Path(row["image_path"]).name, pix)


class ClassifyDatasetDrawWidget(SimpleCardWidget):

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

        self.dataset_draw_thread = DatasetDrawThread()

        self.vly = QVBoxLayout(self)
        self.vly.addLayout(self.dataset_show_option_hly)
        self.vly.addWidget(self.lw_image)

        self._connect_signals_and_slots()

        self._dataset_df: pd.DataFrame = pd.DataFrame()

        self.max_draw_num = int(self.cmb_dataset_max_num.currentText())
        self.image_resolution = ImageItemSize.MEDIUM
        self.dataset_type = DatasetType.TRAIN
        self.dataset_label = "all"
        self.draw_labels = self.ckb_show_label.isChecked()

    def update_dataset(self, dataset_df: pd.DataFrame):
        self._dataset_df = dataset_df
        self.dataset_draw_thread.set_dataset_label(dataset_df.groupby("label").groups.keys())
        self.cmb_dataset_label.clear()
        self.cmb_dataset_label.addItems(["all"] + list(dataset_df.groupby("label").groups.keys()))
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
        max_screen_side = max(QApplication.primaryScreen().geometry().width(),
                              QApplication.primaryScreen().geometry().height())
        max_image_side = max(pix.width(), pix.height())
        max_side = min(max_image_side, int(max_screen_side * 0.6))
        self.image_tip = ImageTip(pix, QCursor.pos(), max_side)
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
        if self.dataset_type == DatasetType.ALL:
            if self.dataset_label == "all":
                image_paths = self._dataset_df.loc[:, ["image_path", "label"]]
            else:
                image_paths = self._dataset_df[self._dataset_df["label"] ==
                                               self.dataset_label].loc[:, ["image_path", "label"]]
        else:
            data_dict = self._dataset_df[self._dataset_df.type == self.dataset_type.value]
            if self.dataset_label == "all":
                image_paths = data_dict.loc[:, ["image_path", "label"]]
            else:
                image_paths = data_dict[data_dict["label"] == self.dataset_label].loc[:, ["image_path", "label"]]
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


class ClassifyDataset(QWidget):
    load_dataset_finished = Signal(int, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")
        # self.dataset_header = DatasetSplitWidget()
        self.labels_widget = ClassifyDatasetLabelsWidget()
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.setContentsMargins(0, 0, 0, 0)
        # self.vly_dataset_info.addWidget(self.dataset_header)
        self.draw_widget = ClassifyDatasetDrawWidget()

        self.hly_content = QHBoxLayout()
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.hly_content.setSpacing(0)
        self.hly_content.addWidget(self.labels_widget)
        self.hly_content.addWidget(self.draw_widget)

        self._dataset_info: DatasetInfo = DatasetInfo()
        self.vly_dataset_info.addLayout(self.hly_content)
        self._dataset_map = dict()
        self._total_dataset = 0
        self._split_rates = []

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self._dataset_info = dataset_info
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=dataset_info.dataset_id).first()
            self._split_rates = [int(rate) for rate in dataset.split_rate.split("_")]
            self._total_dataset = dataset.dataset_total
        if dataset_info.dataset_status == DatasetStatus.CHECKED:
            dataset_df = load_split_dataset(Path(self._dataset_info.dataset_dir))
            self._load_dataset(dataset_df)
        else:
            self.split_dataset()

    def _load_dataset(self, dataset_df: pd.DataFrame):
        all_num = dataset_df.shape[0]
        train_num = dataset_df.groupby("type").groups[DatasetType.TRAIN.value].size
        val_num = dataset_df.groupby("type").groups[DatasetType.VAL.value].size
        test_num = dataset_df.groupby("type").groups[DatasetType.TEST.value].size
        info = SplitLabelInfo(label="All", all_num=all_num, train_num=train_num, val_num=val_num, test_num=test_num)
        dataset_split_num_info = [info]
        for key, group in dataset_df.groupby("label").groups.items():
            label_df = dataset_df[(dataset_df["label"] == key)]
            label_dataset_num = group.size
            train_num = label_df[label_df["type"] == DatasetType.TRAIN.value].shape[0]
            val_num = label_df[label_df["type"] == DatasetType.VAL.value].shape[0]
            test_num = label_df[label_df["type"] == DatasetType.TEST.value].shape[0]
            dataset_split_num_info.append(SplitLabelInfo(label=key,
                                                         all_num=label_dataset_num,
                                                         train_num=train_num,
                                                         val_num=val_num,
                                                         test_num=test_num))
        self.labels_widget.update_table(self._split_rates, dataset_split_num_info)
        self.draw_widget.update_dataset(dataset_df)
        self.load_dataset_finished.emit(self._total_dataset, self._split_rates)

    @Slot(list)
    def split_dataset(self, split_rates):
        self._split_rates = split_rates
        dataset_df = split_dataset(Path(self._dataset_info.dataset_dir), self._split_rates)
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=self._dataset_info.dataset_id).first()
            dataset.dataset_total = dataset_df.shape[0]
        self._load_dataset(dataset_df)
