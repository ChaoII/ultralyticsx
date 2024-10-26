from datetime import datetime

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
from qfluentwidgets import BodyLabel, FluentStyleSheet, PrimaryPushButton, \
    LineEdit, TextEdit, InfoBar, InfoBarPosition
from qframelesswindow import FramelessDialog
from sqlalchemy import desc
from sqlalchemy.orm import Query

from common.component.file_select_widget import FileSelectWidget
from common.component.model_type_widget import ModelTypeGroupWidget, ModelType
from common.database.db_helper import db_session
from models.models import Project, AnnotationTask
from .types import AnnotationTaskInfo


class NewAnnotationTaskDialog(FramelessDialog):
    annotation_task_created = Signal(AnnotationTaskInfo)

    def __init__(self, parent=None):
        super().__init__()
        self._setUpUi(self.tr("Create project"), parent=parent)

    def _setUpUi(self, title, parent):
        self.titleLabel = QLabel(title, parent)
        self.setFixedSize(400, 300)

        self.yesButton = PrimaryPushButton(text=self.tr('Create'))
        self.cancelButton = QPushButton(text=self.tr('Cancel'))
        self.yesButton.setFixedWidth(120)
        self.cancelButton.setFixedWidth(120)

        self.vly_title = QVBoxLayout()
        self.vly_title.setSpacing(12)
        self.vly_title.setContentsMargins(24, 24, 24, 24)
        self.vly_title.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addStretch(1)
        self.hly_btn.addWidget(self.yesButton)
        self.hly_btn.addWidget(self.cancelButton)
        self.hly_btn.setSpacing(12)
        self.hly_btn.setContentsMargins(24, 24, 24, 24)

        self.lbl_name = BodyLabel(text=self.tr("Task name:"))
        self.le_name = LineEdit()
        self.le_name.setMaxLength(16)
        self.lbl_description = BodyLabel(text=self.tr("Task description:"))
        self.ted_description = TextEdit()
        self.lbl_type = BodyLabel(text=self.tr("model type:"))
        self.model_type = ModelTypeGroupWidget()
        self.lbl_image_dir = BodyLabel(text=self.tr("image directory:"))
        self.image_dir_select = FileSelectWidget()
        self.lbl_annotation_dir = BodyLabel(text=self.tr("annotation directory:"))
        self.annotation_dir_select = FileSelectWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.model_type)
        self.fly_content.addRow(self.lbl_image_dir, self.image_dir_select)
        self.fly_content.addRow(self.lbl_annotation_dir, self.annotation_dir_select)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(9)
        self.vBoxLayout.setContentsMargins(12, 0, 12, 0)
        self.vBoxLayout.addLayout(self.vly_title, 1)
        self.vBoxLayout.addLayout(self.fly_content)

        self.vBoxLayout.addLayout(self.hly_btn)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.annotation_task_info = AnnotationTaskInfo()

        self._initWidget()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.model_type.model_type_selected.connect(self._on_annotation_task_type_selected)
        self.ted_description.textChanged.connect(self._on_description_text_changed)
        self.image_dir_select.path_selected.connect(self._on_image_dir_selected)
        self.annotation_dir_select.path_selected.connect(self._on_annotation_dir_selected)

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

    def _initWidget(self):
        self._setQss()
        # fixes https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues/19
        self.yesButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        self.yesButton.setFocus()
        self.yesButton.clicked.connect(self._onYesButtonClicked)
        self.cancelButton.clicked.connect(self._onCancelButtonClicked)

    def _onCancelButtonClicked(self):
        self.reject()

    def _onYesButtonClicked(self):
        with db_session(True) as session:
            projects: Query = session.query(Project).filter_by(project_name=self.le_name.text().strip())
            if len(projects.all()) > 0:
                InfoBar.error(
                    title='',
                    content=self.tr("Project name is existing"),
                    orient=Qt.Orientation.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=-1,
                    parent=self
                )
                return
        self.accept()
        self.annotation_task_info.annotation_task_id = self.get_task_id()
        self.annotation_task_info.annotation_task_name = self.le_name.text()
        self.annotation_task_info.annotation_task_description = self.ted_description.toPlainText()
        self.annotation_task_info.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.annotation_task_created.emit(self.annotation_task_info)

    @staticmethod
    def get_task_id() -> str:
        with db_session() as session:
            latest_task: AnnotationTask = session.query(AnnotationTask).order_by(desc(AnnotationTask.task_id)).first()
            if latest_task is None:
                task_id = "A000001"
            else:
                task_id = f"A{int(latest_task.task_id[1:]) + 1:06d}"
        return task_id

    def _setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.cancelButton.setObjectName('cancelButton')
        FluentStyleSheet.DIALOG.apply(self)
        self.yesButton.adjustSize()
        self.cancelButton.adjustSize()

    def setContentCopyable(self, isCopyable: bool):
        """ set whether the content is copyable """
        if isCopyable:
            self.titleLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
        else:
            self.titleLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.NoTextInteraction)
