from collections import Counter
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Slot, Qt, QSize, Signal
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QSizePolicy, QFileDialog, QFormLayout, QSplitter)
from pyqtgraph import PlotItem
from qfluentwidgets import HeaderCardWidget, BodyLabel, LineEdit, PrimaryPushButton, FluentIcon, TextEdit, \
    StateToolTip, Theme, isDarkTheme

import core
from settings import cfg
from common.utils import *
from .data_convert_thread import DataConvertThread, LoadDatasetInfo
from .dataset_show_widget import DatasetDrawWidget

SMALL = QSize(60, 60)
MEDIUM = QSize(120, 120)
LARGE = QSize(200, 200)
RESOLUTIONS = [SMALL, MEDIUM, LARGE]
DATASET_TYPES = ["train", "val", "test"]


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


class DataProcessWidget(QWidget):
    dataset_process_finished = Signal(str)

    def __init__(self, parent=None):
        super(DataProcessWidget, self).__init__(parent=parent)
        self.setObjectName("dataset_process")

        self.select_card = SelectDatasetCard(self)
        self.btn_data_valid = PrimaryPushButton(FluentIcon.UPDATE, self.tr('data valid'))

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.dataset_info_widget = QWidget()
        self.plot_dataset_info_widget = QWidget()

        self.vly_dataset_info = QVBoxLayout()
        hly_dataset_info = QHBoxLayout()
        fly_dataset_info1 = QFormLayout()
        fly_dataset_info2 = QFormLayout()
        fly_dataset_info3 = QFormLayout()
        fly_dataset_info1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fly_dataset_info2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fly_dataset_info3.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.pg_widget = pg.GraphicsLayoutWidget(show=False)
        self.pg_widget.setBackground((33, 39, 54))

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

        fly_dataset_info1.addRow(self.lbl_train_image_num, self.le_train_image_num)
        fly_dataset_info2.addRow(self.lbl_train_obj_num, self.le_train_obj_num)
        fly_dataset_info1.addRow(self.lbl_val_image_num, self.le_val_image_num)
        fly_dataset_info2.addRow(self.lbl_val_obj_num, self.le_val_obj_num)
        fly_dataset_info1.addRow(self.lbl_test_image_num, self.le_test_image_num)
        fly_dataset_info2.addRow(self.lbl_test_obj_num, self.le_test_obj_num)
        fly_dataset_info3.addRow(self.lbl_dataset_config_path, self.le_dataset_config_path)
        fly_dataset_info3.addRow(self.lbl_dataset_labels, self.ted_dataset_labels)

        hly_dataset_info.addLayout(fly_dataset_info1)
        hly_dataset_info.addLayout(fly_dataset_info2)
        self.vly_dataset_info.addWidget(self.pg_widget)
        self.vly_dataset_info.addLayout(hly_dataset_info)
        self.vly_dataset_info.addLayout(fly_dataset_info3)

        self.dataset_info_widget.setLayout(self.vly_dataset_info)
        self.dataset_draw_widget = DatasetDrawWidget()
        self.splitter.addWidget(self.dataset_info_widget)
        self.splitter.addWidget(self.dataset_draw_widget)

        v_layout = QVBoxLayout(self)

        v_layout.addWidget(self.select_card)
        v_layout.addWidget(self.btn_data_valid)
        v_layout.addWidget(self.splitter)

        self.state_tool_tip = None

        self.dataset_info = None

        self.data_convert_thread = DataConvertThread()
        self._connect_signals_and_slot()
        self._set_chart_style()

    def _connect_signals_and_slot(self):
        cfg.themeChanged.connect(self._on_theme_changed)
        self.btn_data_valid.clicked.connect(self.data_valid)
        self.select_card.dataset_file_changed.connect(self._on_update_dataset)
        self.data_convert_thread.dataset_resolve_finished.connect(self._on_dataset_resolve_finished)
        self.dataset_process_finished.connect(core.EventManager().on_dataset_process_finished)

    @Slot(str)
    def _on_update_dataset(self, dataset_path: str):
        self.data_convert_thread.set_dataset_path(dataset_path)

    @Slot(LoadDatasetInfo)
    def _on_dataset_resolve_finished(self, dataset_info: LoadDatasetInfo):
        self.dataset_info = dataset_info
        self.le_train_image_num.setText(str(len(dataset_info.train_images)))
        self.le_train_obj_num.setText(str(len(dataset_info.train_boxes)))
        self.le_val_image_num.setText(str(len(dataset_info.val_images)))
        self.le_val_obj_num.setText(str(len(dataset_info.val_boxes)))
        self.le_test_image_num.setText(str(len(dataset_info.test_images)))
        self.le_test_obj_num.setText(str(len(dataset_info.test_boxes)))
        self.le_dataset_config_path.setText(dataset_info.dst_yaml_path)
        self.ted_dataset_labels.append("\n".join(f"{k}: {v}" for k, v in dataset_info.labels.items()))
        self.draw_dataset_chart(dataset_info)
        self.dataset_draw_widget.draw_images(dataset_info)
        self.dataset_process_finished.emit(dataset_info.dst_yaml_path)

        # 数据转换完成，显示状态信息
        self.state_tool_tip.setContent(
            self.tr('data converting is completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None

    def draw_dataset_chart(self, dataset_info: LoadDatasetInfo):
        cls = []
        boxes = []
        cls.extend(dataset_info.train_cls)
        cls.extend(dataset_info.val_cls)
        cls.extend(dataset_info.test_cls)
        boxes.extend(dataset_info.train_boxes)
        boxes.extend(dataset_info.val_boxes)
        boxes.extend(dataset_info.test_boxes)
        cls = np.array(cls, np.float32)

        # set custom axis tick
        axis = pg.AxisItem(orientation="bottom")
        tuple_list = [(key, value) for key, value in dataset_info.labels.items()]
        axis.setTicks([tuple_list])
        plt: PlotItem = self.pg_widget.addPlot(axisItems={"bottom": axis})
        plt.showGrid(x=False, y=False)
        # set custom legend
        # legend = pg.LegendItem(offset=(-1, 1))
        # legend.setParentItem(plt)
        for element, count in Counter(cls).items():
            color = generate_random_color()
            bg1 = pg.BarGraphItem(x=element, height=count, width=0.4, pen=invert_color(color), brush=color)

            # 计算标签位置（这里简单地将标签放在柱子上方中央，你可能需要根据实际情况调整）
            bg1.setToolTip(str(count))
            plt.addItem(bg1)
            # 创建TextItem并添加到绘图窗口中
            text_item = pg.TextItem(f'{count:.2f}', anchor=(0.5, 1.2), color=color)  # anchor=(0.5, 0)表示文本中心在指定位置
            print(text_item.pixelHeight())
            text_item.setPos(element, count)  # 设置文本位置
            plt.addItem(text_item)

            # disable legend
            # legend.addItem(bg1, dataset_info.labels[element])
        # set custom axis label
        plt.setLabel("left", self.tr("count of label"))
        # plt.setLabel("bottom", self.tr("labels"))

        # add image item
        # image_item = pg.ImageItem()
        # image_item.setImage(np.ones((500, 500, 4), dtype=np.uint8) * 100)
        # plt2: ViewBox = self.pg_widget.addViewBox()
        # plt2.setAspectLocked(True)
        # plt2.setMouseEnabled(x=False, y=False)
        # plt2.disableAutoRange()
        # plt2.addItem(image_item)

        plt.setMouseEnabled(x=False, y=False)
        plt.disableAutoRange()
        plt.hideButtons()
        plt.showAxes(True, showValues=(True, False, False, True))
        # plt.getAxis('bottom').setHeight(0)

    @Slot()
    def data_valid(self):
        self.clear_cache()
        self.data_convert_thread.start()
        # 设置状态工具栏并显示
        self.state_tool_tip = StateToolTip(
            self.tr('data converting'), self.tr('please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()

    def clear_cache(self):
        self.dataset_draw_widget.lw_image.clear()
        self.le_train_image_num.clear()
        self.le_train_obj_num.clear()
        self.le_val_image_num.clear()
        self.le_val_obj_num.clear()
        self.le_test_image_num.clear()
        self.le_test_obj_num.clear()
        self.le_dataset_config_path.clear()
        self.ted_dataset_labels.clear()

    @Slot(Theme)
    def _on_theme_changed(self, theme):
        self._set_chart_style()

    def _set_chart_style(self):
        """ set style sheet """
        if isDarkTheme():
            self.pg_widget.setBackground((33, 39, 54))
        else:
            self.pg_widget.setBackground((249, 249, 249))
