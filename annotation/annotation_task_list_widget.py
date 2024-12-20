from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import Qt, QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QHeaderView, \
    QTableWidgetItem, QWidget
from loguru import logger
from qfluentwidgets import FluentIcon, CaptionLabel, TableWidget, PrimaryPushButton, \
    PopupTeachingTip, TeachingTipTailPosition

from common.component.custom_process_bar import CustomProcessBar
from common.component.delete_ensure_widget import CustomFlyoutView
from common.component.fill_tool_button import FillToolButton
from common.component.tag_widget import TextTagWidget
from common.component.custom_icon import CustomFluentIcon
from common.core.event_manager import signal_bridge
from common.core.content_widget_base import ContentWidgetBase
from common.core.window_manager import window_manager
from common.database.db_helper import db_session
from common.utils.utils import format_datatime, open_directory, str_to_datetime
from models.models import AnnotationTask
from .new_annotation_task_dialog import NewAnnotationTaskDialog
from .types import AnnotationStatus, AnnotationTaskInfo

COLUMN_TASK_ID = 0
COLUMN_TASK_NAME = 1
COLUMN_TASK_STATUS = 2
COLUMN_PROGRESS_BAR = 3
COLUMN_START_TIME = 4
COLUMN_END_TIME = 5
COLUMN_ELAPSED = 6
COLUMN_OPERATION = 7


class OperationWidget(QWidget):
    task_deleted = Signal(str)
    start_annotation = Signal(str)
    open_task_dir = Signal(str)

    def __init__(self, task_id: str):
        super().__init__()
        self.hly_content = QHBoxLayout(self)
        self.btn_annotate = FillToolButton(CustomFluentIcon.ANNOTATION)
        self.btn_delete = FillToolButton(FluentIcon.DELETE)
        self.btn_delete.set_background_color(QColor("#E61919"))
        self.btn_delete.set_icon_color(QColor(0, 0, 0))
        self.btn_open = FillToolButton(FluentIcon.FOLDER)

        self.hly_content.addStretch(1)
        self.hly_content.addWidget(self.btn_annotate)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_delete)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_open)
        self.hly_content.addStretch(1)
        self._connect_signals_and_slots()
        self.task_id = task_id

    def _connect_signals_and_slots(self):
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        self.btn_annotate.clicked.connect(self._on_annotation_clicked)
        self.btn_open.clicked.connect(self._on_open_clicked)

    def _on_annotation_clicked(self):
        self.start_annotation.emit(self.task_id)

    def _on_open_clicked(self):
        self.open_task_dir.emit(self.task_id)

    def _on_delete_clicked(self):
        self.view = CustomFlyoutView(content=self.tr("Are you sure to delete this task?"))
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
            self.task_deleted.emit(self.task_id)
        self.popup_tip.close()


class AnnotationTaskTableWidget(TableWidget):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(8)
        self.setRowCount(24)
        # self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalHeaderLabels([
            self.tr('Task ID'), self.tr('Task name'), self.tr('Task status'), self.tr("Annotation progress"),
            self.tr('Start time'), self.tr('End time'), self.tr("Elapsed"), self.tr("Operation")
        ])
        self.setColumnWidth(COLUMN_TASK_ID, 130)
        self.horizontalHeader().setSectionResizeMode(COLUMN_TASK_NAME, QHeaderView.ResizeMode.ResizeToContents)
        self.setColumnWidth(COLUMN_TASK_STATUS, 100)
        self.horizontalHeader().setSectionResizeMode(COLUMN_PROGRESS_BAR, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(COLUMN_START_TIME, 156)
        self.setColumnWidth(COLUMN_END_TIME, 156)
        self.setColumnWidth(COLUMN_ELAPSED, 100)
        self.setColumnWidth(COLUMN_OPERATION, 120)


class AnnotationTaskListWidget(ContentWidgetBase):
    start_annotation_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("annotation_task_list_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hly_btn = QHBoxLayout()
        self.btn_create_task = PrimaryPushButton(FluentIcon.ADD, self.tr("Create task"))
        self.hly_btn.addWidget(self.btn_create_task)
        self.hly_btn.addStretch(1)
        self.tb_task = AnnotationTaskTableWidget()
        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.tb_task)
        self._connect_signals_and_slots()
        self._task_id_to_row_index = dict()
        self.update_widget()

    def _connect_signals_and_slots(self):
        self.btn_create_task.clicked.connect(self._on_create_annotation_task_clicked)

    def update_widget(self):
        self.tb_task.clearContents()
        with db_session(auto_commit_exit=True) as session:
            tasks: list[AnnotationTask] = session.query(AnnotationTask).all()
            self.tb_task.setRowCount(len(tasks))
            for row_index, task in enumerate(tasks):
                self._task_id_to_row_index[task.task_id] = row_index
                item0 = QTableWidgetItem(task.task_id)
                item1 = QTableWidgetItem(task.task_name)
                item2 = TextTagWidget(AnnotationStatus(task.task_status).name,
                                      *AnnotationStatus(task.task_status).color)
                item3 = CustomProcessBar()
                item4 = QTableWidgetItem(format_datatime(task.start_time))
                item5 = QTableWidgetItem(format_datatime(task.end_time))
                item6 = QTableWidgetItem(task.elapsed)
                item7 = OperationWidget(task.task_id)

                item7.task_deleted.connect(self._on_delete_task)
                item7.start_annotation.connect(self._on_start_annotation)
                item7.open_task_dir.connect(self._on_open_annotation_dir)

                item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.tb_task.setItem(row_index, COLUMN_TASK_ID, item0)
                self.tb_task.setItem(row_index, COLUMN_TASK_NAME, item1)
                self.tb_task.setCellWidget(row_index, COLUMN_TASK_STATUS, item2)
                self.tb_task.setCellWidget(row_index, COLUMN_PROGRESS_BAR, item3)
                self.tb_task.setItem(row_index, COLUMN_START_TIME, item4)
                self.tb_task.setItem(row_index, COLUMN_END_TIME, item5)
                self.tb_task.setItem(row_index, COLUMN_ELAPSED, item6)
                self.tb_task.setCellWidget(row_index, COLUMN_OPERATION, item7)
                item3.set_max_value(task.total)
                item3.set_value(task.labeled_num)
                if task.task_status == AnnotationStatus.Initialing.value:
                    item3.set_pause(True)
                elif task.task_status == AnnotationStatus.Annotating.value:
                    item3.set_error(True)
                elif task.task_status == AnnotationStatus.AnnoFinished.value:
                    item3.resume()

    @Slot(str)
    def _on_delete_task(self, task_id):
        with db_session() as session:
            task = session.query(AnnotationTask).filter_by(task_id=task_id).first()
            session.delete(task)
        self.update_widget()

    @Slot(str)
    def _on_start_annotation(self, task_id):
        self.start_annotation_clicked.emit(task_id)

    @Slot(str)
    def _on_open_annotation_dir(self, task_id):
        with db_session() as session:
            task: AnnotationTask = session.query(AnnotationTask).filter_by(task_id=task_id).first()
            directory = Path(task.image_dir)
        if directory.exists():
            open_directory(directory)

    @Slot()
    def _on_create_annotation_task_clicked(self):
        self.new_annotation_dialog = NewAnnotationTaskDialog(parent=window_manager.find_window("main_widget"))
        self.new_annotation_dialog.annotation_task_created.connect(self._on_add_new_annotation_task)
        self.new_annotation_dialog.exec()

    @Slot(AnnotationTaskInfo)
    def _on_add_new_annotation_task(self, annotation_task_info: AnnotationTaskInfo):
        new_annotation_task_row = AnnotationTask(
            task_id=annotation_task_info.annotation_task_id,
            task_name=annotation_task_info.annotation_task_name,
            task_description=annotation_task_info.annotation_task_description,
            model_type=annotation_task_info.model_type.value,
            start_time=datetime.now(),
            task_status=AnnotationStatus.Initialing.value,
            image_dir=annotation_task_info.image_dir,
            annotation_dir=annotation_task_info.annotation_dir,
            create_time=str_to_datetime(annotation_task_info.create_time),
        )
        # 这里想获取新增后的id,需要refresh数据，就不能在上下文里提交
        with db_session(True) as session:
            session.add(new_annotation_task_row)
        self.update_widget()
