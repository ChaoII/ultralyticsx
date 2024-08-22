import os
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import BreadcrumbBar

from common.db_helper import db_session
from models.models import Project, Task
from home.project.new_project import ProjectInfo
from home.project.project_widget import ProjectWidget
from home.task.task_detail_widget import TaskDetailWidget
from home.task.task_list_widget import TaskWidget


class HomeWidget(QWidget):
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        self.setObjectName("home_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.breadcrumbBar = BreadcrumbBar(self)
        self.stackedWidget = QStackedWidget(self)
        self.project_widget = ProjectWidget()
        self.task_widget = TaskWidget()
        self.task_detail_widget = TaskDetailWidget()

        self.stackedWidget.addWidget(self.project_widget)
        self.stackedWidget.addWidget(self.task_widget)
        self.stackedWidget.addWidget(self.task_detail_widget)
        self.stackedWidget.setCurrentWidget(self.project_widget)
        self.breadcrumbBar.addItem(self.project_widget.objectName(), self.tr("All projects"))

        self.vly.addWidget(self.breadcrumbBar)
        self.vly.addWidget(self.stackedWidget)
        self._on_connect_signals_and_slots()

    def _on_connect_signals_and_slots(self):
        self.project_widget.project_detail_clicked.connect(self._on_project_detail_clicked, )
        self.breadcrumbBar.currentItemChanged.connect(self._on_bread_bar_item_changed)
        self.task_widget.create_task_clicked.connect(self._on_create_task_clicked)
        self.task_widget.view_task_clicked.connect(self._on_view_task_clicked)

    @Slot(ProjectInfo)
    def _on_project_detail_clicked(self, project_info: ProjectInfo):
        self.stackedWidget.setCurrentWidget(self.task_widget)
        self.breadcrumbBar.addItem(self.task_widget.objectName(), project_info.project_name)
        self.task_widget.set_data(project_info.project_id)

    @Slot()
    def _on_create_task_clicked(self):
        print("===", self.sender())
        self.stackedWidget.setCurrentWidget(self.task_detail_widget)
        self.breadcrumbBar.addItem(self.task_detail_widget.objectName(), self.tr("Create Task"))
        with db_session() as session:
            project: Project = session.query(Project).filter_by(project_id=self.task_widget.project_id).first()
            worker_dir = project.worker_dir
            project_id = self.task_widget.project_id
            task_id = self.task_widget.get_task_id(Path(worker_dir) / project_id)
            os.makedirs(Path(worker_dir) / project_id / task_id, exist_ok=True)

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
