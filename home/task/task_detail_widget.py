from PySide6.QtWidgets import QWidget, QGridLayout, QFormLayout, QVBoxLayout
from qfluentwidgets import BodyLabel, ComboBox, themeColor
from sqlalchemy import and_

from common.collapsible_widget import CollapsibleWidget
from common.custom_icon import CustomFluentIcon
from common.db_helper import db_session
from common.model_type_widget import ModelType
from dataset.types import DatasetStatus
from models.models import Dataset, Task


class DatasetSelectWidget(QWidget):
    def __init__(self, task_id: str, parent=None):
        super().__init__(parent=parent)
        self.gly = QGridLayout(self)
        self.fly = QFormLayout()

        self.lbl_select_dataset = BodyLabel(self.tr("Select dataset: "), self)
        self.cmb_select_dataset = ComboBox()

        self.gly.addWidget(self.lbl_select_dataset, 0, 0)
        self.gly.addWidget(self.cmb_select_dataset, 0, 1)
        self._task_id = task_id

        self._init_data()

    def _init_data(self):
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_id).first()
            model_type = ModelType(task.project.model_type)
        self.cmb_select_dataset.setIcon(model_type.icon.icon(color=themeColor()))
        self.cmb_select_dataset.setPlaceholderText(self.tr(f"Please select a [{model_type.name}] dataset"))
        with db_session() as session:
            datasets: list[Dataset] = session.query(Dataset) \
                .filter(and_(Dataset.model_type == model_type.value,
                             Dataset.dataset_status == DatasetStatus.CHECKED.value)) \
                .all()
            for index, dataset in enumerate(datasets):
                self.cmb_select_dataset.addItem(dataset.dataset_name, model_type.icon, userData=dataset)
                self.cmb_select_dataset.setCurrentIndex(-1)

    def _connect_signals_and_slots(self):
        self.cmb_select_dataset.currentTextChanged(self._on_select_dataset_text_changed)

    def _on_select_dataset_text_changed(self, text):
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_id).first()
            task.dataset_id = text


class TaskDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("task_detail")
        self.csp_select_dataset = CollapsibleWidget(self.tr("Select Dataset"))
        self.vly = QVBoxLayout(self)
        self.vly.addWidget(self.csp_select_dataset)
        self.vly.addStretch(1)
        self._task_id = ""

    def on_update_data(self, task_id):
        self._task_id = task_id
        self.csp_select_dataset.set_content_widget(DatasetSelectWidget(task_id))
