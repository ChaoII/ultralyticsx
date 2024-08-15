import enum
import os
from datetime import datetime
from pathlib import Path
import re
from qfluentwidgets import ElevatedCardWidget, BodyLabel, Dialog, MessageBoxBase, FluentStyleSheet, PrimaryPushButton, \
    TextWrap, LineEdit, TextEdit
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
from qframelesswindow import FramelessDialog
from PySide6.QtWidgets import QFrame, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, Slot
from common.file_select_widget import DirSelectWidget
from settings import cfg
from .project_type_widget import ProjectTypeItemWidget, ProjectTypeGroupWidget
from .project_type_widget import ProjectType


class ProjectInfo:
    project_name: str
    project_id: str
    project_description: str
    project_type: ProjectType = ProjectType.CLASSIFY
    worker_dir: str
    create_time: str


class NewProject(FramelessDialog):
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

        self.lbl_name = BodyLabel(text=self.tr("project name:"))
        self.le_name = LineEdit()
        self.lbl_description = BodyLabel(text=self.tr("project description:"))
        self.ted_description = TextEdit()
        self.lbl_type = BodyLabel(text=self.tr("project type:"))
        self.project_type = ProjectTypeGroupWidget()
        self.lbl_worker_dir = BodyLabel(text=self.tr("worker directory:"))
        self.workdir_select = DirSelectWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.project_type)
        self.fly_content.addRow(self.lbl_worker_dir, self.workdir_select)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(9)
        self.vBoxLayout.setContentsMargins(12, 0, 12, 0)
        self.vBoxLayout.addLayout(self.vly_title, 1)
        self.vBoxLayout.addLayout(self.fly_content)

        self.vBoxLayout.addLayout(self.hly_btn)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.project_info = ProjectInfo()
        self.project_info.worker_dir = cfg.get(cfg.workspace_folder)
        self.workdir_select.le_dir.setText(self.project_info.worker_dir)

        self._initWidget()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.project_type.project_type_selected.connect(self._on_project_type_selected)
        self.workdir_select.dir_selected.connect(self._on_workdir_selected)

    @Slot(str)
    def _on_workdir_selected(self, worker_idr):
        self.project_info.worker_dir = worker_idr

    @Slot(ProjectType)
    def _on_project_type_selected(self, project_type: ProjectType):
        self.project_info.project_type = project_type

    def _initWidget(self):
        self._setQss()
        # fixes https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues/19
        self.yesButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()

        self._adjustText()

        self.yesButton.clicked.connect(self._onYesButtonClicked)
        self.cancelButton.clicked.connect(self._onCancelButtonClicked)

    def _adjustText(self):
        if self.isWindow():
            if self.parent():
                w = max(self.titleLabel.width(), self.parent().width())
                chars = max(min(w / 9, 140), 30)
            else:
                chars = 100
        else:
            w = max(self.titleLabel.width(), self.window().width())
            chars = max(min(w / 9, 100), 30)

    def _onCancelButtonClicked(self):
        self.reject()
        self.cancelSignal.emit()

    def _onYesButtonClicked(self):
        self.accept()
        self.project_info.project_name = self.le_name.text()
        self.project_info.project_description = self.ted_description.toPlainText()
        self.project_info.project_id = self._get_project_id()
        self.project_info.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.project_created.emit(self.project_info)

    def _get_project_id(self) -> str:
        project_id = f"P{0:06d}"
        for item in Path(self.project_info.worker_dir).iterdir():
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
