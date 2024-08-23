import os
import shutil
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import Qt, QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QHeaderView, \
    QTableWidgetItem, QWidget, QAbstractItemView, QFormLayout
from qfluentwidgets import isDarkTheme, FluentIcon, CaptionLabel, TableWidget, PrimaryPushButton, PopupTeachingTip, \
    TeachingTipTailPosition, BodyLabel, ComboBox
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query

from common.db_helper import db_session
from common.delete_ensure_widget import CustomFlyoutView
from common.fill_tool_button import FillToolButton
from common.model_type_widget import ModelType
from common.tag_widget import TextTagWidget
from common.utils import format_datatime, open_directory
from dataset.new_dataset_dialog import NewDatasetDialog, DatasetInfo
from models.models import Dataset
from settings import cfg


class DatasetStatus(Enum):
    WAIT_IMPORT = 0
    CHECKED = 1
    CHECK_FAILED = 2

    @property
    def color(self):
        _color_map = {
            DatasetStatus.WAIT_IMPORT: QColor("#ff6600"),
            DatasetStatus.CHECKED: QColor("#0d5f07"),
            DatasetStatus.CHECK_FAILED: QColor("#ff3333"),
        }
        if isDarkTheme():
            _color_map = {
                DatasetStatus.WAIT_IMPORT: QColor("#ffa366"),
                DatasetStatus.CHECKED: QColor("#66ff66"),
                DatasetStatus.CHECK_FAILED: QColor("#ff9999"),
            }
        return _color_map[self]


class OperationWidget(QWidget):
    dataset_deleted = Signal(str)
    dataset_detail = Signal(str)
    open_dataset_dir = Signal(str)

    def __init__(self, dataset_id: str):
        super().__init__()
        self.hly_content = QHBoxLayout(self)
        self.btn_import = FillToolButton(FluentIcon.CARE_UP_SOLID)
        self.btn_view = FillToolButton(FluentIcon.VIEW)
        self.btn_delete = FillToolButton(FluentIcon.DELETE)
        self.btn_delete.set_background_color(QColor("#E61919"))
        self.btn_delete.set_icon_color(QColor(0, 0, 0))
        self.btn_open = FillToolButton(FluentIcon.FOLDER)

        self.hly_content.addStretch(1)
        self.hly_content.addWidget(self.btn_import)
        self.hly_content.addWidget(self.btn_view)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_delete)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_open)
        self.hly_content.addStretch(1)

        self._connect_signals_and_slots()

        self.dataset_id = dataset_id
        self._init_btn_status()

    def _init_btn_status(self):
        with db_session(auto_commit_exit=True) as session:
            dataset: Dataset = session.query(Dataset).filter_by(dataset_id=self.dataset_id).first()
            if dataset.dataset_status == DatasetStatus.CHECKED.value:
                self._set_checked_status(True)
            else:
                self._set_checked_status(False)

    def _set_checked_status(self, check_status: bool):
        if check_status:
            self.btn_import.setVisible(False)
            self.btn_view.setVisible(True)
        else:
            self.btn_import.setVisible(True)
            self.btn_view.setVisible(False)

    def _connect_signals_and_slots(self):
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        self.btn_view.clicked.connect(self._on_view_clicked)
        self.btn_open.clicked.connect(self._on_open_clicked)

    def _on_view_clicked(self):
        self.dataset_detail.emit(self.dataset_id)

    def _on_open_clicked(self):
        self.open_dataset_dir.emit(self.dataset_id)

    def _on_delete_clicked(self):
        self.view = CustomFlyoutView(content=self.tr("Are you sure to delete this dataset?"))
        self.popup_tip = PopupTeachingTip.make(
            target=self.btn_delete,
            view=self.view,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=-1,
            parent=self
        )
        self.view.accept_status.connect(self._on_ensure_delete_item)

    @Slot(bool)
    def _on_ensure_delete_item(self, accepted):
        if accepted:
            self.dataset_deleted.emit(self.dataset_id)
        self.popup_tip.close()


class DatasetTableWidget(TableWidget):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(6)
        self.setRowCount(24)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalHeaderLabels([
            self.tr("Dataset ID"), self.tr("Dataset name"), self.tr("Model type"),
            self.tr("Create time"), self.tr("Dataset Status"), self.tr("Operation")
        ])
        self.setColumnWidth(0, 100)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 160)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)


class DatasetListWidget(QWidget):
    create_dataset_clicked = Signal()
    view_dataset_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("dataset_list_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hly_btn = QHBoxLayout()
        self.btn_create_dataset = PrimaryPushButton(FluentIcon.ADD, self.tr("Create task"))

        self.lbl_type = BodyLabel(self.tr("type:"), self)
        self.cmb_type = ComboBox()
        self.cmb_type.setMinimumWidth(160)
        self.cmb_type.addItems([self.tr("All type"),
                                self.tr("Classify"),
                                self.tr("Detection"),
                                self.tr("Segmentation"),
                                self.tr("OBB"),
                                self.tr("Pose")])

        self.lbl_sort = BodyLabel(self.tr("sort:"), self)
        self.cmb_sort = ComboBox()
        self.cmb_sort.setMinimumWidth(160)
        self.cmb_sort.addItems([self.tr("time ascending"),
                                self.tr("time descending"),
                                self.tr("name ascending"),
                                self.tr("name descending")])

        self.fly_type = QFormLayout()
        self.fly_type.addRow(self.lbl_type, self.cmb_type)
        self.fly_sort = QFormLayout()
        self.fly_sort.addRow(self.lbl_sort, self.cmb_sort)

        self.hly_btn.addWidget(self.btn_create_dataset)
        self.hly_btn.addStretch(1)
        self.hly_btn.addLayout(self.fly_type)
        self.hly_btn.addLayout(self.fly_sort)
        self.tb_dataset = DatasetTableWidget()
        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.tb_dataset)
        self._connect_signals_and_slots()
        self._load_dataset_data()

    def _connect_signals_and_slots(self):
        self.btn_create_dataset.clicked.connect(self._on_create_dataset_clicked)
        cfg.themeChanged.connect(self._on_theme_changed)
        self.cmb_sort.currentIndexChanged.connect(self._load_dataset_data)
        self.cmb_type.currentIndexChanged.connect(self._load_dataset_data)

    def _on_theme_changed(self):
        for row in range(self.tb_dataset.rowCount()):
            item_model_type = self.tb_dataset.cellWidget(row, 2)
            if isinstance(item_model_type, TextTagWidget):
                model_type = ModelType.__members__.get(item_model_type.text(), None)
                if model_type:
                    item_model_type.set_color(model_type.color)

            item_dataset_status = self.tb_dataset.cellWidget(row, 4)
            if isinstance(item_dataset_status, TextTagWidget):
                dataset_status = DatasetStatus.__members__.get(item_dataset_status.text(), None)
                if dataset_status:
                    item_dataset_status.set_color(dataset_status.color)

    def _load_dataset_data(self):
        self.tb_dataset.clearContents()
        field = Dataset.dataset_name
        order = asc
        if self.cmb_sort.currentIndex() == 0:
            field = Dataset.create_time
            order = asc
        if self.cmb_sort.currentIndex() == 1:
            field = Dataset.create_time
            order = desc
        if self.cmb_sort.currentIndex() == 2:
            field = Dataset.dataset_name
            order = asc
        if self.cmb_sort.currentIndex() == 3:
            field = Dataset.dataset_name
            order = desc

        with db_session(auto_commit_exit=True) as session:
            if self.cmb_type.currentIndex() == 0:
                query: Query = session.query(Dataset)
            else:
                query: Query = session.query(Dataset).filter_by(model_type=self.cmb_type.currentIndex() - 1)
            datasets: list[Dataset] = query.order_by(order(field)).all()
            for i, dataset in enumerate(datasets):
                item0 = QTableWidgetItem(dataset.dataset_id)
                item1 = QTableWidgetItem(dataset.dataset_name)
                item2 = TextTagWidget(ModelType(dataset.model_type).name, ModelType(dataset.model_type).color)

                item3 = QTableWidgetItem(format_datatime(dataset.create_time))
                item4 = TextTagWidget(DatasetStatus(dataset.dataset_status).name,
                                      DatasetStatus(dataset.dataset_status).color)
                item5 = OperationWidget(dataset.dataset_id)

                item5.dataset_deleted.connect(self._on_delete_dataset)
                item5.dataset_detail.connect(self._on_view_dataset)
                item5.open_dataset_dir.connect(self._on_open_dataset_dir)

                item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item3.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.tb_dataset.setItem(i, 0, item0)
                self.tb_dataset.setItem(i, 1, item1)
                self.tb_dataset.setCellWidget(i, 2, item2)
                self.tb_dataset.setItem(i, 3, item3)
                self.tb_dataset.setCellWidget(i, 4, item4)
                self.tb_dataset.setCellWidget(i, 5, item5)

    def _on_create_dataset_clicked(self):
        self.new_dataset_dialog = NewDatasetDialog(self)
        self.new_dataset_dialog.dataset_created.connect(self._on_create_dataset)
        self.new_dataset_dialog.exec()

    @Slot(DatasetInfo)
    def _on_create_dataset(self, dataset_info: DatasetInfo):
        # 创建任务路径
        with db_session() as session:
            os.makedirs(dataset_info.dataset_dir, exist_ok=True)
            dataset = Dataset(
                dataset_id=dataset_info.dataset_id,
                dataset_name=dataset_info.dataset_name,
                model_type=dataset_info.model_type.value,
                dataset_description=dataset_info.dataset_description,
                dataset_status=0,
                dataset_dir=dataset_info.dataset_dir
            )
            session.add(dataset)
        self._load_dataset_data()
        self.create_dataset_clicked.emit()

    @Slot(str)
    def _on_delete_dataset(self, dataset_id):
        with db_session(auto_commit_exit=True) as session:
            dataset: Dataset = session.query(Dataset).filter_by(dataset_id=dataset_id).first()
            directory = dataset.dataset_dir
            session.delete(dataset)
        shutil.rmtree(directory)
        self._load_dataset_data()

    @Slot(str)
    def _on_view_dataset(self, task_id):
        self.view_dataset_clicked.emit(task_id)

    @Slot(str)
    def _on_open_dataset_dir(self, dataset_id):
        with db_session() as session:
            dataset: Dataset = session.query(Dataset).filter_by(dataset_id=dataset_id).first()
            directory = Path(dataset.dataset_dir)
        open_directory(directory)
