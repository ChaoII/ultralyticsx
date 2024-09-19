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

from common.database.db_helper import db_session
from common.model_type_widget import ModelType
from common.model_type_widget import ModelTypeGroupWidget
from common.utils import format_datatime
from dataset.types import DatasetInfo
from models.models import Dataset
from settings import cfg


class NewDatasetDialog(FramelessDialog):
    dataset_created = Signal(DatasetInfo)
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
        self.model_type = ModelTypeGroupWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.model_type)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(9)
        self.vBoxLayout.setContentsMargins(12, 0, 12, 0)
        self.vBoxLayout.addLayout(self.vly_title, 1)
        self.vBoxLayout.addLayout(self.fly_content)

        self.vBoxLayout.addLayout(self.hly_btn)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.dataset_info = DatasetInfo()

        self.dataset_root_dir = Path(cfg.get(cfg.workspace_folder)) / "dataset"
        os.makedirs(self.dataset_root_dir, exist_ok=True)
        self._initWidget()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.model_type.model_type_selected.connect(self._on_project_type_selected)
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

    @Slot(ModelType)
    def _on_project_type_selected(self, model_type: ModelType):
        self.dataset_info.model_type = model_type

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
            datasets: Query = session.query(Dataset).filter_by(dataset_name=self.le_name.text().strip())
            if len(datasets.all()) > 0:
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
        self.dataset_info.dataset_dir = (
                Path(self.dataset_root_dir) / self.dataset_info.dataset_id).resolve().as_posix()
        self.dataset_created.emit(self.dataset_info)

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
