import os
import re
import shutil
from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import Qt, QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QHeaderView, \
    QTableWidgetItem, QWidget
from loguru import logger
from qfluentwidgets import FluentIcon, CaptionLabel, TableWidget, PrimaryPushButton, \
    PopupTeachingTip, TeachingTipTailPosition

from common.core import event_manager
from common.component.custom_icon import CustomFluentIcon
from common.component.custom_process_bar import CustomProcessBar
from common.database.db_helper import db_session
from common.database.task_helper import db_get_project_id
from common.component.delete_ensure_widget import CustomFlyoutView
from common.component.fill_tool_button import FillToolButton
from common.component.tag_widget import TextTagWidget
from common.utils.utils import format_datatime, open_directory
from common.core.content_widget_base import ContentWidgetBase
from models.models import Task, Project
from ..types import TaskStatus

COLUMN_TASK_ID = 0
COLUMN_PROJECT_NAME = 1
COLUMN_TASK_STATUS = 2
COLUMN_PROGRESS_BAR = 3
COLUMN_START_TIME = 4
COLUMN_END_TIME = 5
COLUMN_ELAPSED = 6
COLUMN_OPERATION = 7


class OperationWidget(QWidget):
    task_deleted = Signal(str)
    task_detail = Signal(str)
    open_task_dir = Signal(str)

    def __init__(self, task_id: str):
        super().__init__()
        self.hly_content = QHBoxLayout(self)
        self.btn_view = FillToolButton(CustomFluentIcon.DETAIL1)
        self.btn_delete = FillToolButton(FluentIcon.DELETE)
        self.btn_delete.set_background_color(QColor("#E61919"))
        self.btn_delete.set_icon_color(QColor(0, 0, 0))
        self.btn_open = FillToolButton(FluentIcon.FOLDER)

        self.hly_content.addStretch(1)
        self.hly_content.addWidget(self.btn_view)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_delete)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_open)
        self.hly_content.addStretch(1)

        self._connect_signals_and_slots()

        self.task_id = task_id

    def _connect_signals_and_slots(self):
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        self.btn_view.clicked.connect(self._on_view_clicked)
        self.btn_open.clicked.connect(self._on_open_clicked)

    def _on_view_clicked(self):
        self.task_detail.emit(self.task_id)

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


class TaskTableWidget(TableWidget):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(8)
        self.setRowCount(24)
        # self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalHeaderLabels([
            self.tr('Task ID'), self.tr('Project name'), self.tr('Task status'), self.tr("Train progress"),
            self.tr('Start time'), self.tr('End time'), self.tr("Elapsed"), self.tr("Operation")
        ])
        self.setColumnWidth(COLUMN_TASK_ID, 130)
        self.horizontalHeader().setSectionResizeMode(COLUMN_PROJECT_NAME, QHeaderView.ResizeMode.ResizeToContents)
        self.setColumnWidth(COLUMN_TASK_STATUS, 100)
        self.horizontalHeader().setSectionResizeMode(COLUMN_PROGRESS_BAR, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(COLUMN_START_TIME, 156)
        self.setColumnWidth(COLUMN_END_TIME, 156)
        self.setColumnWidth(COLUMN_ELAPSED, 100)
        self.setColumnWidth(COLUMN_OPERATION, 120)


class TaskListWidget(ContentWidgetBase):
    view_task_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("task_list_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hly_btn = QHBoxLayout()
        self.btn_create_task = PrimaryPushButton(FluentIcon.ADD, self.tr("Create task"))
        self.hly_btn.addWidget(self.btn_create_task)
        self.hly_btn.addStretch(1)
        self.tb_task = TaskTableWidget()
        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.tb_task)
        self._current_project_id = ""
        self._connect_signals_and_slots()
        self._task_id_to_row_index = dict()

    def _connect_signals_and_slots(self):
        self.btn_create_task.clicked.connect(self._on_create_task)
        event_manager.signal_bridge.train_status_changed.connect(self._on_train_status_changed)

    def set_data(self, project_id: str):
        self._current_project_id = project_id
        self.update_widget()

    def update_widget(self):
        self.tb_task.clearContents()
        with db_session(auto_commit_exit=True) as session:
            tasks: list[Task] = session.query(Task).filter_by(project_id=self._current_project_id).all()
            self.tb_task.setRowCount(len(tasks))
            for row_index, task in enumerate(tasks):
                self._task_id_to_row_index[task.task_id] = row_index

                item0 = QTableWidgetItem(task.task_id)
                item1 = QTableWidgetItem(task.project.project_name)
                item2 = TextTagWidget(TaskStatus(task.task_status).name, *TaskStatus(task.task_status).color)
                item3 = CustomProcessBar()
                item4 = QTableWidgetItem(format_datatime(task.start_time))
                item5 = QTableWidgetItem(format_datatime(task.end_time))
                item6 = QTableWidgetItem(task.elapsed)
                item7 = OperationWidget(task.task_id)

                item7.task_deleted.connect(self._on_delete_task)
                item7.task_detail.connect(self._on_view_task)
                item7.open_task_dir.connect(self._on_open_task_dir)

                item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.tb_task.setItem(row_index, COLUMN_TASK_ID, item0)
                self.tb_task.setItem(row_index, COLUMN_PROJECT_NAME, item1)
                self.tb_task.setCellWidget(row_index, COLUMN_TASK_STATUS, item2)
                self.tb_task.setCellWidget(row_index, COLUMN_PROGRESS_BAR, item3)
                self.tb_task.setItem(row_index, COLUMN_START_TIME, item4)
                self.tb_task.setItem(row_index, COLUMN_END_TIME, item5)
                self.tb_task.setItem(row_index, COLUMN_ELAPSED, item6)
                self.tb_task.setCellWidget(row_index, COLUMN_OPERATION, item7)

                item3.set_value(task.epoch)
                item3.set_max_value(task.epochs)
                if task.task_status == TaskStatus.TRN_PAUSE.value:
                    item3.set_pause(True)
                elif task.task_status == TaskStatus.TRN_FAILED.value:
                    item3.set_error(True)
                elif task.task_status == TaskStatus.TRN_FINISHED.value:
                    item3.resume()

    @Slot(str, str, TaskStatus)
    def _on_train_status_changed(self, task_id: str, epoch: int, epochs: int, start_time: str, end_time: str,
                                 elapsed: str, task_status: TaskStatus):
        project_id = db_get_project_id(task_id)
        if project_id != self._current_project_id:
            return
        row_index = self._task_id_to_row_index.get(task_id)
        if row_index is None:
            logger.warning(f"task_id: {task_id} not found in table")
            return
        item_task_status = self.tb_task.cellWidget(row_index, COLUMN_TASK_STATUS)
        item_start_time = self.tb_task.item(row_index, COLUMN_START_TIME)
        item_end_time = self.tb_task.item(row_index, COLUMN_END_TIME)
        item_elapsed = self.tb_task.item(row_index, COLUMN_ELAPSED)
        item_bar = self.tb_task.cellWidget(row_index, COLUMN_PROGRESS_BAR)

        if isinstance(item_bar, CustomProcessBar) and isinstance(item_task_status, TextTagWidget):
            if task_status == TaskStatus.TRAINING:
                item_bar.set_max_value(epochs)
                item_bar.set_value(epoch)
                item_task_status.set_text(TaskStatus.TRAINING.name)
                item_task_status.set_color(*TaskStatus.TRAINING.color)
                item_start_time.setText(start_time)
                item_end_time.setText("")
                item_elapsed.setText("")
            elif task_status == TaskStatus.TRN_PAUSE:
                item_task_status.set_text(TaskStatus.TRN_PAUSE.name)
                item_task_status.set_color(*TaskStatus.TRN_PAUSE.color)
                item_bar.set_pause(True)
            elif task_status == TaskStatus.TRN_FAILED:
                item_task_status.set_text(TaskStatus.TRN_FAILED.name)
                item_task_status.set_color(*TaskStatus.TRN_FAILED.color)
                item_bar.set_error(True)
            elif task_status == TaskStatus.TRN_FINISHED:
                item_task_status.set_text(TaskStatus.TRN_FINISHED.name)
                item_task_status.set_color(*TaskStatus.TRN_FINISHED.color)
                item_bar.resume()
                item_end_time.setText(end_time)
                item_elapsed.setText(elapsed)
            self.update()

    def get_task_id(self, project_dir: Path) -> str:
        task_id = f"T{self._current_project_id[1:]}{0:06d}"
        for item in project_dir.iterdir():
            if item.is_dir() and re.match(r'^T\d{12}$', item.name):
                task_id = f"T{int(item.name[1:]) + 1:012d}"
        return task_id

    @Slot(str)
    def _on_delete_task(self, task_id):
        with db_session() as session:
            task = session.query(Task).filter_by(task_id=task_id).first()
            directory = Path(task.project.project_dir) / task_id
            session.delete(task)
        try:
            shutil.rmtree(directory)
        except Exception as e:
            logger.error(f"Failed to delete directory {directory}: {e}")
        self.set_data(self._current_project_id)

    @Slot(str)
    def _on_view_task(self, task_id):
        self.view_task_clicked.emit(task_id)

    @Slot(str)
    def _on_open_task_dir(self, task_id):
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=task_id).first()
            directory = Path(task.project.project_dir) / task_id
        open_directory(directory)

    @Slot()
    def _on_create_task(self):
        # 创建任务路径
        with db_session() as session:
            project: Project = session.query(Project).filter_by(project_id=self._current_project_id).first()
            project_dir = Path(project.project_dir)
            task_id = self.get_task_id(project_dir)
            try:
                os.makedirs(project_dir / task_id, exist_ok=True)
                task = Task(
                    task_id=task_id,
                    task_status=TaskStatus.INITIALIZING.value,
                    epoch=0,
                    epochs=0
                )
                project.tasks.append(task)
            except Exception as e:
                logger.error(f"Failed to create task directory {project_dir / task_id}: {e}")
        self.set_data(self._current_project_id)
