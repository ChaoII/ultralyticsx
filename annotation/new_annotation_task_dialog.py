from datetime import datetime

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QFormLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, LineEdit, TextEdit, InfoBar, InfoBarPosition, MessageBoxBase, SubtitleLabel
from sqlalchemy import desc
from sqlalchemy.orm import Query

from common.component.file_select_widget import FileSelectWidget
from common.component.model_type_widget import ModelTypeGroupWidget, ModelType
from common.database.db_helper import db_session
from models.models import Project, AnnotationTask
from .types import AnnotationTaskInfo


class NewAnnotationTaskDialog(MessageBoxBase):
    annotation_task_created = Signal(AnnotationTaskInfo)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(self.tr("Create annotation task"), parent=parent)

    def _setUpUi(self, title, parent):
        self.titleLabel = SubtitleLabel(title, parent)
        self.buttonLayout.insertStretch(0, 1)
        self.yesButton.setText(self.tr("Create"))
        self.yesButton.setFixedWidth(120)
        self.cancelButton.setFixedWidth(120)

        self.hly_title = QHBoxLayout()
        self.hly_title.addWidget(self.titleLabel)
        self.hly_title.addStretch(1)

        self.lbl_name = BodyLabel(text=self.tr("Task name:"))
        self.le_name = LineEdit()
        self.le_name.setMaxLength(16)
        self.lbl_description = BodyLabel(text=self.tr("Task description:"))
        self.ted_description = TextEdit()
        self.ted_description.setMaximumHeight(120)
        self.lbl_type = BodyLabel(text=self.tr("model type:"))
        self.model_type = ModelTypeGroupWidget()
        self.lbl_image_dir = BodyLabel(text=self.tr("image directory:"))
        self.image_dir_select = FileSelectWidget()
        self.lbl_annotation_dir = BodyLabel(text=self.tr("annotation directory:"))
        self.annotation_dir_select = FileSelectWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setContentsMargins(0, 0, 0, 0)
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.model_type)
        self.fly_content.addRow(self.lbl_image_dir, self.image_dir_select)
        self.fly_content.addRow(self.lbl_annotation_dir, self.annotation_dir_select)

        self.viewLayout.addLayout(self.hly_title)
        self.viewLayout.addLayout(self.fly_content)
        self.annotation_task_info = AnnotationTaskInfo()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.model_type.model_type_selected.connect(self._on_annotation_task_type_selected)
        self.ted_description.textChanged.connect(self._on_description_text_changed)
        self.image_dir_select.path_selected.connect(self._on_image_dir_selected)
        self.annotation_dir_select.path_selected.connect(self._on_annotation_dir_selected)
        self.yesButton.clicked.connect(self._on_create_button_clicked)

    def _on_create_button_clicked(self):
        with db_session(True) as session:
            projects: Query = session.query(Project).filter_by(project_name=self.le_name.text().strip())
            if len(projects.all()) > 0:
                InfoBar.error(
                    title='',
                    content=self.tr("Task name is existing"),
                    orient=Qt.Orientation.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=-1,
                    parent=self
                )
                return

        self.annotation_task_info.annotation_task_id = self.get_task_id()
        self.annotation_task_info.annotation_task_name = self.le_name.text()
        self.annotation_task_info.annotation_task_description = self.ted_description.toPlainText()
        self.annotation_task_info.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.annotation_task_created.emit(self.annotation_task_info)
        self.accept()

    @Slot(str)
    def _on_description_text_changed(self):
        if len(self.ted_description.toPlainText()) > 100:
            InfoBar.error(
                title='',
                content=self.tr("Over maximum length 100, current length is: ") + str(
                    len(self.ted_description.toPlainText())),
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self
            )
            # 截断文本到最大长度
            self.ted_description.setPlainText(self.ted_description.toPlainText()[:100])

    @Slot(str)
    def _on_image_dir_selected(self, image_dir):
        self.annotation_task_info.image_dir = image_dir

    @Slot(str)
    def _on_annotation_dir_selected(self, annotation_dir):
        self.annotation_task_info.annotation_dir = annotation_dir

    @Slot(ModelType)
    def _on_annotation_task_type_selected(self, annotation_task_type: ModelType):
        self.annotation_task_info.model_type = annotation_task_type

    @staticmethod
    def get_task_id() -> str:
        with db_session() as session:
            latest_task: AnnotationTask = session.query(AnnotationTask).order_by(desc(AnnotationTask.task_id)).first()
            if latest_task is None:
                task_id = "A000001"
            else:
                task_id = f"A{int(latest_task.task_id[1:]) + 1:06d}"
        return task_id
