import os
import re
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
from qfluentwidgets import BodyLabel, FluentStyleSheet, PrimaryPushButton, \
    LineEdit, TextEdit, InfoBar, InfoBarPosition
from qframelesswindow import FramelessDialog
from sqlalchemy.orm import Query

from common.db_helper import db_session
from common.file_select_widget import DirSelectWidget
from common.model_type_widget import ModelTypeGroupWidget, ModelType
from models.models import Project
from settings import cfg


class ProjectInfo:
    project_name: str
    project_id: str
    project_description: str
    model_type: ModelType = ModelType.CLASSIFY
    project_dir: str
    create_time: str


class NewProjectDialog(FramelessDialog):
    project_created = Signal(ProjectInfo)
    cancelSignal = Signal()

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

        self.lbl_name = BodyLabel(text=self.tr("Project name:"))
        self.le_name = LineEdit()
        self.le_name.setMaxLength(16)
        self.lbl_description = BodyLabel(text=self.tr("Project description:"))
        self.ted_description = TextEdit()
        self.lbl_type = BodyLabel(text=self.tr("model type:"))
        self.model_type = ModelTypeGroupWidget()
        self.lbl_workspace_dir = BodyLabel(text=self.tr("workspace directory:"))
        self.workdir_select = DirSelectWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.model_type)
        self.fly_content.addRow(self.lbl_workspace_dir, self.workdir_select)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(9)
        self.vBoxLayout.setContentsMargins(12, 0, 12, 0)
        self.vBoxLayout.addLayout(self.vly_title, 1)
        self.vBoxLayout.addLayout(self.fly_content)

        self.vBoxLayout.addLayout(self.hly_btn)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.project_info = ProjectInfo()
        self.workdir_select.le_dir.setText(cfg.get(cfg.workspace_folder))
        self.project_root_dir = Path(cfg.get(cfg.workspace_folder)) / "project"
        os.makedirs(self.project_root_dir, exist_ok=True)
        self._initWidget()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.model_type.model_type_selected.connect(self._on_project_type_selected)
        self.workdir_select.dir_selected.connect(self._on_workdir_selected)
        self.ted_description.textChanged.connect(self._on_description_text_changed)

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
    def _on_workdir_selected(self, workspace_idr):
        self.project_info.workspace_dir = workspace_idr

    @Slot(ModelType)
    def _on_project_type_selected(self, project_type: ModelType):
        self.project_info.model_type = project_type

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
        self.cancelSignal.emit()

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
        self.project_info.project_id = self._get_project_id()
        self.project_info.project_name = self.le_name.text()
        self.project_info.project_description = self.ted_description.toPlainText()
        self.project_info.project_dir = (self.project_root_dir / self.project_info.project_id).resolve().as_posix()
        self.project_info.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.project_created.emit(self.project_info)

    def _get_project_id(self) -> str:
        project_id = f"P{0:06d}"
        for item in self.project_root_dir.iterdir():
            if item.is_dir() and re.match(r'^P\d{6}$', item.name):
                project_id = f"P{int(item.name[1:]) + 1:06d}"
        return project_id

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
