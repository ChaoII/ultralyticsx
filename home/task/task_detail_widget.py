from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QFormLayout, QVBoxLayout
from qfluentwidgets import BodyLabel, ComboBox, themeColor
from sqlalchemy import and_

from common.collapsible_widget import CollapsibleWidgetItem, ToolBox
from common.custom_icon import CustomFluentIcon
from common.custom_scroll_widget import CustomScrollWidget
from common.db_helper import db_session
from common.model_type_widget import ModelType
from dataset.types import DatasetStatus
from home.task.train_setting_widget import TrainParameterWidget
from models.models import Dataset, Task


class DatasetSelectWidget(CollapsibleWidgetItem):
    def __init__(self, parent=None):
        super().__init__(self.tr("▌Select Dataset"), parent=parent)
        self.content_widget = QWidget(self)

        self.lbl_select_dataset = BodyLabel(self.tr("Select dataset: "), self)
        self.cmb_select_dataset = ComboBox()
        self.cmb_select_dataset.setPlaceholderText(self.tr(f"Please select a dataset"))
        self.cmb_select_dataset.setCurrentIndex(-1)
        self.cmb_select_dataset.setMaximumWidth(400)
        self.lbl_all_num = BodyLabel()
        self.lbl_train_set_num = BodyLabel()
        self.lbl_val_set_num = BodyLabel()
        self.lbl_test_set_num = BodyLabel()

        self.dataset_detail = QWidget(self)
        self.fly = QFormLayout(self.dataset_detail)
        self.fly.setHorizontalSpacing(40)
        self.fly.setVerticalSpacing(15)
        self.fly.addRow(BodyLabel(self.tr("all: "), self), self.lbl_all_num)
        self.fly.addRow(BodyLabel(self.tr("training set: "), self), self.lbl_train_set_num)
        self.fly.addRow(BodyLabel(self.tr("validation set: "), self), self.lbl_val_set_num)
        self.fly.addRow(BodyLabel(self.tr("test set: "), self), self.lbl_test_set_num)
        self.fly_content = QFormLayout(self.content_widget)
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.setHorizontalSpacing(40)
        self.fly_content.addRow(self.lbl_select_dataset, self.cmb_select_dataset)
        self.fly_content.addRow("", self.dataset_detail)
        self._connect_signals_and_slots()
        self._task_id = ""
        self.set_content_widget(self.content_widget)

    def set_task_id(self, task_id):
        self.cmb_select_dataset.clear()
        self.cmb_select_dataset.setEnabled(True)
        self.dataset_detail.setVisible(False)
        self._task_id = task_id
        self._init_data()

    def _init_data(self):
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_id).first()
            model_type = ModelType(task.project.model_type)
            self.cmb_select_dataset.setIcon(model_type.icon.icon(color=themeColor()))
            dataset_id = task.dataset_id
        if dataset_id:
            self.cmb_select_dataset.addItem(dataset_id, model_type.icon.icon(themeColor()))
            self.cmb_select_dataset.setCurrentIndex(0)
            self.cmb_select_dataset.setEnabled(False)
            self._load_current_dataset_info()
            return
        with db_session() as session:
            datasets: list[Dataset] = session.query(Dataset).filter(
                and_(Dataset.model_type == model_type.value,
                     Dataset.dataset_status == DatasetStatus.CHECKED.value)).all()
            for index, dataset in enumerate(datasets):
                self.cmb_select_dataset.addItem(dataset.dataset_id,
                                                model_type.icon.icon(color=themeColor()),
                                                userData=dataset)
                self.cmb_select_dataset.setCurrentIndex(-1)
        self.cmb_select_dataset.currentIndexChanged.connect(self._on_select_dataset_index_changed)

    def _connect_signals_and_slots(self):
        pass

    def _load_current_dataset_info(self):
        self.dataset_detail.setVisible(True)
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_id).first()
            train_rate, val_rate, test_rate = task.dataset.split_rate.split("_")
            dataset_total = task.dataset.dataset_total
            train_num = round(int(train_rate) * dataset_total / 100)
            val_num = round(int(val_rate) * dataset_total / 100)
            test_num = dataset_total - train_num - val_num
        self.lbl_all_num.setText(str(dataset_total))
        self.lbl_train_set_num.setText(str(train_num))
        self.lbl_val_set_num.setText(str(val_num))
        self.lbl_test_set_num.setText(str(test_num))

    @Slot(int)
    def _on_select_dataset_index_changed(self, index: int):
        if index != -1:
            with db_session() as session:
                task: Task = session.query(Task).filter_by(task_id=self._task_id).first()
                task.dataset_id = self.cmb_select_dataset.currentText()
            self._load_current_dataset_info()


class TaskDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("task_detail")
        self.tool_box = ToolBox()

        self.dataset_select_widget = DatasetSelectWidget()
        self.train_parameter_widget = TrainParameterWidget(parent=self)
        self.tool_box.add_item(self.dataset_select_widget)
        self.tool_box.add_item(self.train_parameter_widget)

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

    def update_data(self, task_id):
        self.dataset_select_widget.set_task_id(task_id)
        self.train_parameter_widget.set_task_id(task_id)
