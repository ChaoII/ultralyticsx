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
from common.utils import format_datatime
from models.models import Project
from settings import cfg
from .project_type_widget import ProjectType
from .project_type_widget import ProjectTypeGroupWidget


class DatasetInfo:
    dataset_name: str
    dataset_id: str
    dataset_description: str
    dataset_type: ProjectType = ProjectType.CLASSIFY
    create_time: str


class NewDatasetDialog(FramelessDialog):
    project_created = Signal(DatasetInfo)
    cancelSignal = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self._setUpUi(self.tr("Create dataset"), parent=parent)

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

        self.lbl_name = BodyLabel(text=self.tr("Dataset name:"))
        self.le_name = LineEdit()
        self.le_name.setMaxLength(16)
        self.lbl_description = BodyLabel(text=self.tr("Dataset description:"))
        self.ted_description = TextEdit()
        self.lbl_type = BodyLabel(text=self.tr("Dataset type:"))
        self.project_type = ProjectTypeGroupWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.project_type)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(9)
        self.vBoxLayout.setContentsMargins(12, 0, 12, 0)
        self.vBoxLayout.addLayout(self.vly_title, 1)
        self.vBoxLayout.addLayout(self.fly_content)

        self.vBoxLayout.addLayout(self.hly_btn)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.dataset_info = DatasetInfo()
        self.dataset_root_dir = Path(cfg.get(cfg.workspace_folder)) / "dataset"
        self._initWidget()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.project_type.project_type_selected.connect(self._on_project_type_selected)
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

    @Slot(ProjectType)
    def _on_project_type_selected(self, dataset_info: ProjectType):
        self.dataset_info.project_type = dataset_info

    def _initWidget(self):
        self._setQss()
        # fixes https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues/19
        self.yesButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()

        self._adjustText()

        self.yesButton.clicked.connect(self._onYesButtonClicked)
        self.cancelButton.clicked.connect(self._onCancelButtonClicked)

        if not self.dataset_root_dir.exists():
            os.makedirs(self.dataset_root_dir, exist_ok=True)

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
        with db_session(True) as session:
            projects: Query = session.query(Project).filter_by(project_name=self.le_name.text().strip())
            if len(projects.all()) > 0:
                InfoBar.error(
                    title='',
                    content=self.tr("Dataset name is existing"),
                    orient=Qt.Orientation.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=-1,
                    parent=self
                )
                return
        self.accept()
        self.dataset_info.dataset_name = self.le_name.text()
        self.dataset_info.dataset_description = self.ted_description.toPlainText()
        self.dataset_info.dataset_id = self.get_dataset_id(self.dataset_root_dir)
        self.dataset_info.create_time = format_datatime(datetime.now())
        self.project_created.emit(self.dataset_info)

    @staticmethod
    def get_dataset_id(dataset_dir: Path) -> str:
        dataset_id = f"D{0:06d}"
        for item in dataset_dir.iterdir():
            if item.is_dir() and re.match(r'^D\d{6}$', item.name):
                dataset_id = f"D{int(item.name[1:]) + 1:06d}"
        return dataset_id

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
