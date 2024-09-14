from PySide6.QtCore import Slot, Qt, Signal
from PySide6.QtWidgets import QWidget, QFormLayout
from qfluentwidgets import BodyLabel, ComboBox, themeColor, PrimaryPushButton, FluentIcon
from sqlalchemy import and_

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_icon import CustomFluentIcon
from common.db_helper import db_session
from dataset.types import DatasetStatus
from home.types import TaskInfo, TaskStatus
from models.models import Dataset, Task


class DatasetSelectWidget(CollapsibleWidgetItem):
    dataset_selected_clicked = Signal(TaskInfo)

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
        self.btn_next_step = PrimaryPushButton(icon=CustomFluentIcon.NEXT, text=self.tr("Next"))
        self.btn_next_step.setFixedWidth(120)
        self.dataset_detail = QWidget(self)
        self.fly = QFormLayout(self.dataset_detail)
        self.fly.setHorizontalSpacing(40)
        self.fly.setVerticalSpacing(15)
        self.fly.addRow(BodyLabel(self.tr("all: "), self), self.lbl_all_num)
        self.fly.addRow(BodyLabel(self.tr("training set: "), self), self.lbl_train_set_num)
        self.fly.addRow(BodyLabel(self.tr("validation set: "), self), self.lbl_val_set_num)
        self.fly.addRow(BodyLabel(self.tr("test set: "), self), self.lbl_test_set_num)
        self.fly.addRow("", self.btn_next_step)
        self.fly_content = QFormLayout(self.content_widget)
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.setHorizontalSpacing(40)
        self.fly_content.addRow(self.lbl_select_dataset, self.cmb_select_dataset)
        self.fly_content.addRow("", self.dataset_detail)
        self._is_select_dataset_connect_signal_and_slots = False
        self._connect_signals_and_slots()
        self._task_info: TaskInfo | None = None
        self.set_content_widget(self.content_widget)

    def set_task_info(self, task_info: TaskInfo):
        self.cmb_select_dataset.clear()
        self.cmb_select_dataset.setEnabled(True)
        self.dataset_detail.setVisible(False)
        self._task_info = task_info
        self._init_data()

    def _init_data(self):
        if self._is_select_dataset_connect_signal_and_slots:
            self.cmb_select_dataset.currentIndexChanged.disconnect(self._on_select_dataset_index_changed)
            self._is_select_dataset_connect_signal_and_slots = False
        self.cmb_select_dataset.setIcon(self._task_info.model_type.icon.icon(color=themeColor()))
        if self._task_info.task_status.value >= TaskStatus.DS_SELECTED.value:
            self.cmb_select_dataset.addItem(self._task_info.dataset_id,
                                            self._task_info.model_type.icon.icon(themeColor()))
            self.cmb_select_dataset.setCurrentIndex(0)
            self.cmb_select_dataset.setEnabled(False)
            self._load_current_dataset_info()
            return
        with db_session() as session:
            self.cmb_select_dataset.clear()
            datasets: list[Dataset] = session.query(Dataset).filter(
                and_(Dataset.model_type == self._task_info.model_type.value,
                     Dataset.dataset_status == DatasetStatus.CHECKED.value)).all()

            for index, dataset in enumerate(datasets):
                self.cmb_select_dataset.addItem(dataset.dataset_id,
                                                self._task_info.model_type.icon.icon(color=themeColor()),
                                                userData=dataset)
                self.cmb_select_dataset.setCurrentIndex(-1)
            self.cmb_select_dataset.currentIndexChanged.connect(self._on_select_dataset_index_changed)
            self._is_select_dataset_connect_signal_and_slots = True

    def _connect_signals_and_slots(self):
        self.btn_next_step.clicked.connect(self._on_next_step_clicked)

    def _on_next_step_clicked(self):
        self.dataset_selected_clicked.emit(self._task_info)

    def _load_current_dataset_info(self):
        self.dataset_detail.setVisible(True)
        with db_session() as session:
            task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
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
                task: Task = session.query(Task).filter_by(task_id=self._task_info.task_id).first()
                self._task_info.dataset_id = self.cmb_select_dataset.currentText()
                self._task_info.task_status = TaskStatus.DS_SELECTED
                task.dataset_id = self.cmb_select_dataset.currentText()
                task.task_status = TaskStatus.DS_SELECTED.value
            self._load_current_dataset_info()
