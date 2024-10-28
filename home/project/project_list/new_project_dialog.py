import os
import re
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
from qfluentwidgets import BodyLabel, FluentStyleSheet, PrimaryPushButton, \
    LineEdit, TextEdit, InfoBar, InfoBarPosition, MessageBoxBase, SubtitleLabel
from sqlalchemy.orm import Query

from common.database.db_helper import db_session
from common.component.file_select_widget import FileSelectWidget
from common.component.model_type_widget import ModelTypeGroupWidget, ModelType
from home.types import ProjectInfo
from models.models import Project
from settings import cfg


class NewProjectDialog(MessageBoxBase):
    project_created = Signal(ProjectInfo)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(self.tr("Create project"), parent=parent)

    def _setUpUi(self, title, parent):
        self.titleLabel = SubtitleLabel(title, parent)
        self.buttonLayout.insertStretch(0, 1)
        self.yesButton.setText(self.tr("Create"))
        self.yesButton.setFixedWidth(120)
        self.cancelButton.setFixedWidth(120)

        self.hly_title = QHBoxLayout()
        self.hly_title.addWidget(self.titleLabel)
        self.hly_title.addStretch(1)

        self.lbl_name = BodyLabel(text=self.tr("Project name:"))
        self.le_name = LineEdit()
        self.le_name.setMaxLength(16)
        self.lbl_description = BodyLabel(text=self.tr("Project description:"))
        self.ted_description = TextEdit()
        self.lbl_type = BodyLabel(text=self.tr("model type:"))
        self.model_type = ModelTypeGroupWidget()
        self.lbl_workspace_dir = BodyLabel(text=self.tr("workspace directory:"))
        self.workdir_select = FileSelectWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.model_type)
        self.fly_content.addRow(self.lbl_workspace_dir, self.workdir_select)

        self.viewLayout.addLayout(self.hly_title)
        self.viewLayout.addLayout(self.fly_content)

        self.project_info = ProjectInfo()
        self.workdir_select.setText(cfg.get(cfg.workspace_folder))
        self.project_root_dir = Path(cfg.get(cfg.workspace_folder)) / "project"
        os.makedirs(self.project_root_dir, exist_ok=True)
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.yesButton.clicked.connect(self._on_create_button_clicked)
        self.model_type.model_type_selected.connect(self._on_project_type_selected)
        self.workdir_select.path_selected.connect(self._on_workdir_selected)
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

    def _on_create_button_clicked(self):
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
