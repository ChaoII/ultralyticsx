from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QVBoxLayout

from common.component.collapsible_widget import ToolBox
from common.component.custom_scroll_widget import CustomScrollWidget
from common.database.db_helper import db_session
from common.component.model_type_widget import ModelType
from common.core.content_widget_base import ContentWidgetBase
from models.models import TrainTask
from .task_detail.model_val_widget import ModelValWidget
from .task_detail.model_parameter_widget import ModelParameterWidget
from .task_detail.model_dataset_widget import ModelDatasetWidget
from .task_detail.model_export_widget import ModelExportWidget
from .task_detail.model_train_widget import ModelTrainWidget
from .task_detail.model_predict_widget import ModelPredictWidget
from ..types import TrainTaskInfo, TrainTaskStatus


class TaskDetailWidget(ContentWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("task_detail_widget")
        self.tool_box = ToolBox()

        self.model_dataset_widget = ModelDatasetWidget()
        self.model_parameter_widget = ModelParameterWidget()
        self.model_train_widget = ModelTrainWidget()
        self.model_val_widget = ModelValWidget()
        self.model_export_widget = ModelExportWidget()
        self.model_predict_widget = ModelPredictWidget()
        self.tool_box.add_item(self.model_dataset_widget)
        self.tool_box.add_item(self.model_parameter_widget)
        self.tool_box.add_item(self.model_train_widget)
        self.tool_box.add_item(self.model_val_widget)
        self.tool_box.add_item(self.model_export_widget)
        self.tool_box.add_item(self.model_predict_widget)

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
        self.model_dataset_widget.dataset_selected_clicked.connect(self._on_dataset_selected_clicked)
        self.model_parameter_widget.parameter_config_finished.connect(self._on_parameter_config_finished)
        self.model_parameter_widget.start_training_clicked.connect(self._on_start_training_clicked)
        self.model_train_widget.is_training_signal.connect(self.model_parameter_widget.update_train_btn_status)
        self.model_train_widget.next_step_clicked.connect(self._on_train_finish_and_next_clicked)
        self.model_val_widget.next_step_clicked.connect(self._on_val_finish_and_next_clicked)
        self.model_export_widget.export_model_finished.connect(self._on_model_export_finish)

    @Slot(TrainTaskInfo)
    def _on_dataset_selected_clicked(self, task_info):
        self.tool_box.set_current_item(self.model_parameter_widget)
        self.model_parameter_widget.setEnabled(True)
        self.model_train_widget.set_task_info(task_info)

    @Slot(TrainTaskInfo)
    def _on_parameter_config_finished(self, task_info: TrainTaskInfo):
        self.tool_box.set_current_item(self.model_train_widget)
        self.model_train_widget.setEnabled(True)
        self.model_train_widget.set_task_info(task_info)

    @Slot(TrainTaskInfo)
    def _on_start_training_clicked(self, task_info: TrainTaskInfo):
        self.tool_box.set_current_item(self.model_train_widget)
        self.model_train_widget.setEnabled(True)
        self.model_train_widget.set_task_info(task_info)
        self.model_train_widget.start_train()

    @Slot(TrainTaskInfo)
    def _on_train_finish_and_next_clicked(self, task_info: TrainTaskInfo):
        self.tool_box.set_current_item(self.model_val_widget)
        self.model_val_widget.setEnabled(True)
        self.model_val_widget.set_task_info(task_info)

    def _on_val_finish_and_next_clicked(self, task_info: TrainTaskInfo):
        self.tool_box.set_current_item(self.model_export_widget)
        self.model_export_widget.setEnabled(True)
        self.model_export_widget.set_task_info(task_info)

    @Slot(bool)
    def _on_model_export_finish(self, task_info: TrainTaskInfo):
        self.tool_box.set_current_item(self.model_predict_widget)
        self.model_predict_widget.set_task_info(task_info)

    def update_data(self, task_id):
        self._task_id = task_id
        # 在切换面包屑时会自动调用update_widget()
        # self.update_widget()

    def update_widget(self):
        task_info = TrainTaskInfo()
        with db_session() as session:
            task: TrainTask = session.query(TrainTask).filter_by(task_id=self._task_id).first()
            task_info.task_id = task.task_id
            task_info.dataset_id = task.dataset_id
            task_info.project_id = task.project_id
            task_info.task_status = TrainTaskStatus(task.task_status)
            task_info.model_type = ModelType(task.project.model_type)
            task_info.task_dir = Path(task.project.project_dir) / self._task_id

        if task_info.task_status == TrainTaskStatus.INITIALIZING:
            self.tool_box.set_current_item(self.model_dataset_widget)
            self.model_dataset_widget.setEnabled(True)
            self.model_parameter_widget.setEnabled(False)
            self.model_train_widget.setEnabled(False)
            self.model_val_widget.setEnabled(False)
            self.model_export_widget.setEnabled(False)
            self.model_predict_widget.setEnabled(False)
        if task_info.task_status == TrainTaskStatus.DS_SELECTED:
            self.tool_box.set_current_item(self.model_parameter_widget)
            self.model_dataset_widget.setEnabled(True)
            self.model_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(False)
            self.model_val_widget.setEnabled(False)
            self.model_export_widget.setEnabled(False)
            self.model_predict_widget.setEnabled(False)
        if task_info.task_status.value >= TrainTaskStatus.CFG_FINISHED.value:
            self.tool_box.set_current_item(self.model_train_widget)
            self.model_dataset_widget.setEnabled(True)
            self.model_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(True)
            self.model_val_widget.setEnabled(False)
            self.model_export_widget.setEnabled(False)
            self.model_predict_widget.setEnabled(False)
        if task_info.task_status.value >= TrainTaskStatus.TRN_FINISHED.value:
            self.tool_box.set_current_item(self.model_val_widget)
            self.model_dataset_widget.setEnabled(True)
            self.model_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(True)
            self.model_val_widget.setEnabled(True)
            self.model_export_widget.setEnabled(True)
            self.model_predict_widget.setEnabled(True)
        if task_info.task_status.value >= TrainTaskStatus.VAL_FINISHED.value:
            self.tool_box.set_current_item(self.model_predict_widget)
            self.model_dataset_widget.setEnabled(True)
            self.model_parameter_widget.setEnabled(True)
            self.model_train_widget.setEnabled(True)
            self.model_val_widget.setEnabled(True)
            self.model_export_widget.setEnabled(True)
            self.model_predict_widget.setEnabled(True)

        self.model_dataset_widget.set_task_info(task_info)
        self.model_parameter_widget.set_task_info(task_info)
        self.model_train_widget.set_task_info(task_info)
        self.model_val_widget.set_task_info(task_info)
        self.model_export_widget.set_task_info(task_info)
        self.model_predict_widget.set_task_info(task_info)
