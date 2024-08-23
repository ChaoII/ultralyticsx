import os
import re
import shutil
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Signal, QModelIndex, Slot
from PySide6.QtGui import Qt, QColor, QPalette
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QHeaderView, \
    QStyleOptionViewItem, QTableWidgetItem, QWidget, QAbstractItemView
from qfluentwidgets import isDarkTheme, FluentIcon, CaptionLabel, TableWidget, TableItemDelegate, HyperlinkLabel, \
    setCustomStyleSheet, PrimaryPushButton, PopupTeachingTip, TeachingTipTailPosition

from common.db_helper import db_session
from common.delete_ensure_widget import CustomFlyoutView
from common.fill_tool_button import FillToolButton
from common.tag_widget import TextTagWidget
from common.utils import format_datatime, open_directory
from models.models import Task, Project


class TaskStatus(Enum):
    INITIALIZING = 0
    TRAINING = 1
    TRAIN_FAILED = 2

    @property
    def color(self):
        _color_map = {
            TaskStatus.INITIALIZING: QColor("#ff6600"),
            TaskStatus.TRAINING: QColor("#0d5f07"),
            TaskStatus.TRAIN_FAILED: QColor("#ff3333"),
        }
        if isDarkTheme():
            _color_map = {
                TaskStatus.INITIALIZING: QColor("#ffa366"),
                TaskStatus.TRAINING: QColor("#66ff66"),
                TaskStatus.TRAIN_FAILED: QColor("#ff9999"),
            }
        return _color_map[self]


class OperationWidget(QWidget):
    task_deleted = Signal(str)
    task_detail = Signal(str)
    open_task_dir = Signal(str)

    def __init__(self, task_id: str):
        super().__init__()
        self.hly_content = QHBoxLayout(self)
        self.btn_view = FillToolButton(FluentIcon.VIEW)
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


class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return
        if isDarkTheme():
            option.palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            option.palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        else:
            option.palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.red)
            option.palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.red)


class TaskTableWidget(TableWidget):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(6)
        self.setRowCount(24)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setItemDelegate(CustomTableItemDelegate(self))
        self.setHorizontalHeaderLabels([
            self.tr('Task ID'), self.tr('Project name'), self.tr('Task status'),
            self.tr('Comment'), self.tr('Create time'), self.tr("Operation")
        ])
        self.setColumnWidth(0, 100)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(4, 160)
        self.setColumnWidth(5, 160)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)


class TaskWidget(QWidget):
    create_task_clicked = Signal()
    view_task_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("task_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hly_btn = QHBoxLayout()
        self.btn_create_task = PrimaryPushButton(FluentIcon.ADD, self.tr("Create task"))
        self.hly_btn.addWidget(self.btn_create_task)
        self.hly_btn.addStretch(1)
        self.tb_task = TaskTableWidget()
        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.tb_task)
        self._connect_signals_and_slots()
        self.project_id = ""

    def set_data(self, project_id: str):
        self.tb_task.clearContents()
        self.project_id = project_id
        with db_session(auto_commit_exit=True) as session:
            tasks: list[Task] = session.query(Task).filter_by(project_id=project_id).all()
            for i, task in enumerate(tasks):
                item0 = QTableWidgetItem(task.task_id)
                item1 = QTableWidgetItem(task.project.project_name)
                item2 = TextTagWidget(TaskStatus(task.task_status).name, TaskStatus(task.task_status).color)
                item3 = QTableWidgetItem(task.comment)
                item4 = QTableWidgetItem(format_datatime(task.create_time))
                item5 = OperationWidget(task.task_id)
                item5.task_deleted.connect(self._on_delete_task)
                item5.task_detail.connect(self._on_view_task)
                item5.open_task_dir.connect(self._on_open_task_dir)

                item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.tb_task.setItem(i, 0, item0)
                self.tb_task.setItem(i, 1, item1)
                self.tb_task.setCellWidget(i, 2, item2)
                self.tb_task.setItem(i, 3, item3)
                self.tb_task.setItem(i, 4, item4)
                self.tb_task.setCellWidget(i, 5, item5)

    @staticmethod
    def get_task_id(project_dir: Path) -> str:
        task_id = f"T{0:06d}"
        for item in project_dir.iterdir():
            if item.is_dir() and re.match(r'^T\d{6}$', item.name):
                task_id = f"T{int(item.name[1:]) + 1:06d}"
        return task_id

    def _connect_signals_and_slots(self):
        self.btn_create_task.clicked.connect(self._on_create_task)

    @Slot(str)
    def _on_delete_task(self, task_id):
        with db_session(auto_commit_exit=True) as session:
            task = session.query(Task).filter_by(task_id=task_id).first()
            directory = Path(task.project.workspace_dir) / task.project.project_id / task_id
            session.delete(task)
        shutil.rmtree(directory)
        self.set_data(self.project_id)

    @Slot(str)
    def _on_view_task(self, task_id):
        self.view_task_clicked.emit(task_id)

    @Slot(str)
    def _on_open_task_dir(self, task_id):
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=task_id).first()
            directory = Path(task.project.workspace_dir) / task.project.project_id / task_id
        open_directory(directory)

    @Slot()
    def _on_create_task(self):
        # 创建任务路径
        with db_session() as session:
            project: Project = session.query(Project).filter_by(project_id=self.project_id).first()
            workspace_dir = project.workspace_dir
            task_id = self.get_task_id(Path(workspace_dir) / self.project_id)
            os.makedirs(Path(workspace_dir) / self.project_id / task_id, exist_ok=True)
            task = Task(
                task_id=task_id,
                comment="",
                task_status=0,
            )
            project.tasks.append(task)
        self.set_data(self.project_id)
        self.create_task_clicked.emit()
