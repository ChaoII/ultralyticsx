import os
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import BreadcrumbBar

from common.db_helper import db_session
from models.models import Project, Task
from home.task.task_detail_widget import TaskDetailWidget
from home.task.task_list_widget import TaskWidget


class DatasetWidget(QWidget):
    def __init__(self, parent=None):
        super(DatasetWidget, self).__init__(parent=parent)
        self.setObjectName("dataset_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.breadcrumbBar = BreadcrumbBar(self)
        self.stackedWidget = QStackedWidget(self)
        self.task_widget = TaskWidget()
        self.task_detail_widget = TaskDetailWidget()

        self.stackedWidget.addWidget(self.task_widget)
        self.stackedWidget.addWidget(self.task_detail_widget)
        self.breadcrumbBar.addItem(self.task_widget.objectName(), self.tr("All dataset"))

        self.vly.addWidget(self.breadcrumbBar)
        self.vly.addWidget(self.stackedWidget)
        self._on_connect_signals_and_slots()

    def _on_connect_signals_and_slots(self):
        self.breadcrumbBar.currentItemChanged.connect(self._on_bread_bar_item_changed)
        self.task_widget.create_task_clicked.connect(self._on_create_task_clicked)
        self.task_widget.view_task_clicked.connect(self._on_view_task_clicked)

    @Slot()
    def _on_create_task_clicked(self):
        self.stackedWidget.setCurrentWidget(self.task_detail_widget)
        self.breadcrumbBar.addItem(self.task_detail_widget.objectName(), self.tr("Create Task"))

    @Slot(str)
    def _on_view_task_clicked(self, task_id):
        self.stackedWidget.setCurrentWidget(self.task_detail_widget)
        with db_session(auto_commit_exit=True) as session:
            task: Task = session.query(Task).filter_by(task_id=task_id).first()
            self.breadcrumbBar.addItem(self.task_detail_widget.objectName(), task.task_id)

    @Slot(str)
    def _on_bread_bar_item_changed(self, obj_name):
        obj = self.findChild(QWidget, obj_name)
        if isinstance(obj, QWidget):
            self.stackedWidget.setCurrentWidget(obj)
