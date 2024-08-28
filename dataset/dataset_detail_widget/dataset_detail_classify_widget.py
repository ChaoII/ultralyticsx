import enum
import random
import time
from pathlib import Path

import pandas as pd
from PySide6.QtCore import Slot, Qt, QSize, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QCursor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QListView, QListWidgetItem, QApplication
from qfluentwidgets import SimpleCardWidget, ComboBox, CheckBox, ListWidget

from common.db_helper import db_session
from dataset.dataset_detail_widget.dataset_split_widget import DatasetSplitWidget
from dataset.dataset_detail_widget.label_table_Widget import LabelTableWidget, SplitLabelInfo
from dataset.types import DatasetInfo
from dataset_process.image_tip_widget import ImageTip
from models.models import Dataset


class ImageItemSize(enum.Enum):
    SMALL = QSize(60, 60)
    MEDIUM = QSize(120, 120)
    LARGE = QSize(200, 200)


class DatasetType(enum.Enum):
    ALL = "all"
    TRAIN = "train"
    VAL = "val"
    TEST = "test"


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
        self.image_paths: list[Path] = []

    def set_dataset_path(self, dataset_paths: list[Path]):
        self.image_paths = dataset_paths

    def set_draw_labels_status(self, status: bool):
        self.draw_labels = status

    def set_max_draw_nums(self, max_draw_num: int):
        self.max_draw_num = max_draw_num

    def run(self):
        for index, image_path in enumerate(self.image_paths):
            if index >= self.max_draw_num:
                break
            pix = QPixmap(image_path)
            time.sleep(0.01)
            self.draw_one_image.emit(Path(image_path).name, pix)


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
        self.cmb_dataset_type.setCurrentIndex(0)
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
        self.dataset_type = DatasetType.ALL
        self.dataset_label = "all"
        self.draw_labels = self.ckb_show_label.isChecked()

    def update_dataset(self, dataset_df: pd.DataFrame):
        self._dataset_df = dataset_df
        self.cmb_dataset_label.clear()
        self.cmb_dataset_label.addItems(["all"] + dataset_df.index.to_list())
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
        self.dataset_draw_thread.set_max_draw_nums(int(text))
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
            all_type_df = self._dataset_df.apply(lambda row: [item for sublist in row for item in sublist], axis=1)

            if self.dataset_label == "all":
                image_paths = [item for sublist in all_type_df for item in sublist]
            else:
                image_paths = all_type_df.loc[self.dataset_label]
        else:
            data_dict = self._dataset_df[self.dataset_type.value]
            if self.dataset_label == "all":
                image_paths = [item for sublist in data_dict for item in sublist]
            else:
                image_paths = data_dict.loc[self.dataset_label]

        self.dataset_draw_thread.set_dataset_path(image_paths)
        self.dataset_draw_thread.start()

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


class ClassifyDataset(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")
        self.dataset_header = DatasetSplitWidget()
        self.labels_widget = ClassifyDatasetLabelsWidget()
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.setContentsMargins(0, 0, 0, 0)
        self.vly_dataset_info.addWidget(self.dataset_header)
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

        self._connect_signals_and_slots()

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self._dataset_info = dataset_info
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=dataset_info.dataset_id).first()
            self._split_rates = [int(rate) for rate in dataset.split_rate.split("_")]
        self._parser_dataset(dataset_info)
        self.dataset_header.set_dataset(self._total_dataset, self._split_rates)
        self._split_dataset()

    def _connect_signals_and_slots(self):
        self.dataset_header.split_clicked.connect(self._on_split_clicked)

    @Slot(list)
    def _on_split_clicked(self, split_rates):
        self._split_rates = split_rates
        # 更新拆分比例
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=self._dataset_info.dataset_id).first()
            dataset.split_rate = "_".join([str(rate) for rate in split_rates])
        self._split_dataset()

    def _parser_dataset(self, dataset_info: DatasetInfo):
        self._dataset_map.clear()
        self._total_dataset = 0
        for item in Path(dataset_info.dataset_dir).iterdir():
            if item.is_dir():
                images = list(map(lambda x: x.resolve().as_posix(), item.iterdir()))
                self._dataset_map[item.name] = images
                self._total_dataset += len(images)

    def _split_dataset(self):
        train = dict()
        val = dict()
        test = dict()
        info = SplitLabelInfo(label=self.tr("All"), all_num=self._total_dataset,
                              train_num=round(self._total_dataset * self._split_rates[0] / 100),
                              val_num=round(self._total_dataset * self._split_rates[1] / 100),
                              test_num=round(self._total_dataset * self._split_rates[2] / 100))

        dataset_split_num_info = [info]
        for key, item in self._dataset_map.items():
            label_dataset_num = len(item)
            train_num = round(label_dataset_num * self._split_rates[0] / 100)
            val_num = round(label_dataset_num * self._split_rates[1] / 100)
            test_num = label_dataset_num - train_num - val_num

            label_dataset_index = list(range(len(item)))
            random.shuffle(label_dataset_index)
            train_data = [item[index] for index in label_dataset_index[:train_num]]
            val_data = [item[index] for index in label_dataset_index[train_num:train_num + val_num]]
            test_data = [item[index] for index in label_dataset_index[train_num + val_num:]]

            train.update({key: train_data})
            val.update({key: val_data})
            test.update({key: test_data})

            dataset_split_num_info.append(SplitLabelInfo(label=key,
                                                         all_num=label_dataset_num,
                                                         train_num=train_num,
                                                         val_num=val_num,
                                                         test_num=test_num))

        datasets = dict(train=train, val=val, test=test)
        df_dataset = pd.DataFrame(datasets)
        self.labels_widget.update_table(self._split_rates, dataset_split_num_info)
        self.draw_widget.update_dataset(df_dataset)
