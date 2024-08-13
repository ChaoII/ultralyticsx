from qfluentwidgets import ElevatedCardWidget, BodyLabel, Dialog, MessageBoxBase, FluentStyleSheet, PrimaryPushButton, \
    TextWrap, LineEdit, TextEdit
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
from qframelesswindow import FramelessDialog
from PySide6.QtWidgets import QFrame, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from common.file_select_widget import FileSelectWidget
from .project_type_widget import ProjectTypeWidget


class NewProject(FramelessDialog):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self._setUpUi("1231", parent=parent)

    def _setUpUi(self, title, parent):
        self.titleLabel = QLabel(title, parent)

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
        self.ted_type = ProjectTypeWidget()
        self.lbl_worker_dir = BodyLabel(text=self.tr("worker directory:"))
        self.file_select = FileSelectWidget()
        self.fly_content = QFormLayout()
        self.fly_content.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fly_content.addRow(self.lbl_name, self.le_name)
        self.fly_content.addRow(self.lbl_description, self.ted_description)
        self.fly_content.addRow(self.lbl_type, self.ted_type)
        self.fly_content.addRow(self.lbl_worker_dir, self.file_select)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(9)
        self.vBoxLayout.setContentsMargins(12, 0, 12, 0)
        self.vBoxLayout.addLayout(self.vly_title, 1)
        self.vBoxLayout.addLayout(self.fly_content)

        self.vBoxLayout.addLayout(self.hly_btn)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        self.__initWidget()

    def __initWidget(self):
        self.__setQss()
        # fixes https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues/19
        self.yesButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()

        self._adjustText()

        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.clicked.connect(self.__onCancelButtonClicked)

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

    def __onCancelButtonClicked(self):
        self.reject()
        self.cancelSignal.emit()

    def __onYesButtonClicked(self):
        self.accept()
        self.yesSignal.emit()

    def __setQss(self):
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
