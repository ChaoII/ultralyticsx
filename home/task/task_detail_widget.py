from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QVBoxLayout

from common.collapsible_widget import ToolBox
from common.custom_scroll_widget import CustomScrollWidget
from common.database.db_helper import db_session
from common.model_type_widget import ModelType
from core.content_widget_base import ContentWidgetBase
from home.task.task_detail.dataset_select_widget import DatasetSelectWidget
from home.task.task_detail.model_export_widget import ModelExportWidget
from home.task.task_detail.model_train_widget import ModelTrainWidget
from home.task.task_detail.train_setting_widget import TrainParameterWidget
from home.types import TaskInfo, TaskStatus
from models.models import Task


class TaskDetailWidget(ContentWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("task_detail_widget")
        self.tool_box = ToolBox()

        self.dataset_select_widget = DatasetSelectWidget()
        self.train_parameter_widget = TrainParameterWidget()
        self.model_train_widget = ModelTrainWidget()
        self.model_export_widget = ModelExportWidget()
        self.tool_box.add_item(self.dataset_select_widget)
        self.tool_box.add_item(self.train_parameter_widget)
        self.tool_box.add_item(self.model_train_widget)
        self.tool_box.add_item(self.model_export_widget)

        self.vly = QVBoxLayout()
        self.vly.setContentsMargins(0, 0, 0, 0)
        self.vly.addWidget(self.tool_box)
        # self.vly.addStretch(1)

        self.scroll_area = CustomScrollWidget(orient=Qt.Orientation.Vertical)
        self.scroll_area.setLayout(self.vly)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.setContentsMargins(0, 0, 0, 0)
        self.vly_content.addWidget(self.scroll_area)

        self._task_id = ""

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.dataset_select_widget.dataset_selected_clicked.connect(self._on_dataset_selected_clicked)
        self.train_parameter_widget.parameter_config_finished.connect(self._on_parameter_config_finished)
        self.train_parameter_widget.start_training_clicked.connect(self._on_start_training_clicked)
        self.model_train_widget.is_training_signal.connect(self.train_parameter_widget.update_train_btn_status)
        self.model_train_widget.next_step_clicked.connect(self._on_train_finish_and_next_clicked)
        self.model_export_widget.export_model_finished.connect(self._on_model_export_finish)

    @Slot(TaskInfo)
    def _on_dataset_selected_clicked(self, task_info):
        self.tool_box.set_current_item(self.train_parameter_widget)
        self.train_parameter_widget.setEnabled(True)
        self.model_train_widget.set_task_info(task_info)

    @Slot(TaskInfo)
    def _on_parameter_config_finished(self, task_info: TaskInfo):
        self.tool_box.set_current_item(self.model_train_widget)
        self.model_train_widget.setEnabled(True)
        self.model_train_widget.set_task_info(task_info)

    @Slot(TaskInfo)
    def _on_start_training_clicked(self, task_info: TaskInfo):
        self.tool_box.set_current_item(self.model_train_widget)
        self.model_train_widget.setEnabled(True)
        self.model_train_widget.set_task_info(task_info)
        self.model_train_widget.start_train()

    @Slot(TaskInfo)
    def _on_train_finish_and_next_clicked(self, task_info: TaskInfo):
        self.tool_box.set_current_item(self.model_export_widget)
        self.model_export_widget.setEnabled(True)
        self.model_export_widget.set_task_info(task_info)

    @Slot(bool)
    def _on_model_export_finish(self, is_finished: bool):
        if not is_finished:
            self.model_export_widget.setEnabled(False)
            self.model_train_widget.setEnabled(False)
            self.train_parameter_widget.setEnabled(False)
            self.dataset_select_widget.setEnabled(False)
        else:
            self.model_export_widget.setEnabled(True)
            self.model_train_widget.setEnabled(True)
            self.train_parameter_widget.setEnabled(True)
            self.dataset_select_widget.setEnabled(True)

    def update_data(self, task_id):
        self._task_id = task_id
        self.update_widget()

    def update_widget(self):
        task_info = TaskInfo()
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_id).first()
            task_info.task_id = task.task_id
            task_info.dataset_id = task.dataset_id
            task_info.project_id = task.project_id
            task_info.comment = task.comment
            task_info.task_status = TaskStatus(task.task_status)
            task_info.model_type = ModelType(task.project.model_type)
            task_info.task_dir = Path(task.project.project_dir) / self._task_id

        print("============================================================================================")
        print(task_info.task_status)

        if task_info.task_status == TaskStatus.INITIALIZING:
            self.tool_box.set_current_item(self.dataset_select_widget)
            self.dataset_select_widget.setEnabled(True)
            self.train_parameter_widget.setEnabled(False)
            self.model_train_widget.setEnabled(False)
            self.model_export_widget.setEnabled(False)
        if task_info.task_status == TaskStatus.DS_SELECTED:
            self.tool_box.set_current_item(self.train_parameter_widget)
            self.dataset_select_widget.setEnabled(True)
            self.train_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(False)
            self.model_export_widget.setEnabled(False)
        if task_info.task_status.value >= TaskStatus.CFG_FINISHED.value:
            self.tool_box.set_current_item(self.model_train_widget)
            self.dataset_select_widget.setEnabled(True)
            self.train_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(True)
            self.model_export_widget.setEnabled(False)

        if task_info.task_status.value >= TaskStatus.TRN_FINISHED.value:
            self.tool_box.set_current_item(self.model_export_widget)
            self.dataset_select_widget.setEnabled(True)
            self.train_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(True)
            self.model_export_widget.setEnabled(True)

        self.dataset_select_widget.set_task_info(task_info)
        self.train_parameter_widget.set_task_info(task_info)
        self.model_train_widget.set_task_info(task_info)
        self.model_export_widget.set_task_info(task_info)
