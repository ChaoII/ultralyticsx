from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import BreadcrumbBar

from core.content_widget_base import ContentWidgetBase
from core.interface_base import InterfaceBase
from .project.project_list.new_project_dialog import ProjectInfo
from .project.project_list_widget import ProjectListWidget
from .task.task_detail_widget import TaskDetailWidget
from .task.task_list_widget import TaskListWidget


class HomeWidget(InterfaceBase):

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        self.setObjectName("home_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setContentsMargins(10, 10, 10, 10)
        self.vly.setSpacing(9)
        self.breadcrumbBar = BreadcrumbBar(self)
        self.stackedWidget = QStackedWidget(self)
        self.project_list_widget = ProjectListWidget()
        self.task_list_widget = TaskListWidget()
        self.task_detail_widget = TaskDetailWidget()

        self.stackedWidget.addWidget(self.project_list_widget)
        self.stackedWidget.addWidget(self.task_list_widget)
        self.stackedWidget.addWidget(self.task_detail_widget)
        self.stackedWidget.setCurrentWidget(self.project_list_widget)
        self.breadcrumbBar.addItem(self.project_list_widget.objectName(), self.tr("All projects"))

        self.vly.addWidget(self.breadcrumbBar)
        self.vly.addWidget(self.stackedWidget)
        self._on_connect_signals_and_slots()

    def _on_connect_signals_and_slots(self):
        self.project_list_widget.project_detail_clicked.connect(self._on_project_detail_clicked)
        self.breadcrumbBar.currentItemChanged.connect(self._on_bread_bar_item_changed)
        self.task_list_widget.view_task_clicked.connect(self._on_view_task_clicked)

    @Slot(ProjectInfo)
    def _on_project_detail_clicked(self, project_info: ProjectInfo):
        self.stackedWidget.setCurrentWidget(self.task_list_widget)
        self.breadcrumbBar.addItem(self.task_list_widget.objectName(), project_info.project_name)
        self.task_list_widget.set_data(project_info.project_id)

    @Slot(str)
    def _on_view_task_clicked(self, task_id):
        self.task_detail_widget.update_data(task_id)
        self.stackedWidget.setCurrentWidget(self.task_detail_widget)
        self.breadcrumbBar.addItem(self.task_detail_widget.objectName(), task_id)

    def update_widget(self):
        self.breadcrumbBar.setCurrentItem(self.task_list_widget.objectName())

    @Slot(str)
    def _on_bread_bar_item_changed(self, obj_name):
        obj = self.findChild(QWidget, obj_name)
        if isinstance(obj, ContentWidgetBase):
            self.stackedWidget.setCurrentWidget(obj)
            obj.update_widget()
