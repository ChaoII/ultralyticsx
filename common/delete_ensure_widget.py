from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import FlyoutViewBase, BodyLabel, PrimaryPushButton, PushButton, FluentIcon, InfoBarIcon, \
    TransparentToolButton, LargeTitleLabel, StrongBodyLabel


class CustomFlyoutView(FlyoutViewBase):
    accept_status = Signal(bool)

    def __init__(self, content: str, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.icon = TransparentToolButton(InfoBarIcon.WARNING, parent=self)
        self.icon.setIconSize(QSize(20, 20))
        self.lbl_title = StrongBodyLabel(self.tr("Warning"), self)
        self.lbl_content = BodyLabel(content, self)
        self.btn_ensure = PrimaryPushButton(self.tr('Ensure'), self)
        self.btn_cancel = PushButton(self.tr("Cancel"), self)
        self.btn_ensure.setFixedWidth(120)
        self.btn_cancel.setFixedWidth(120)
        self.hly_content = QHBoxLayout()
        self.hly_content.addWidget(self.icon)
        self.hly_content.addWidget(self.lbl_content)
        self.hly_btn = QHBoxLayout()
        self.hly_btn.addStretch(1)
        self.hly_btn.addWidget(self.btn_ensure)
        self.hly_btn.addWidget(self.btn_cancel)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(self.lbl_title)
        self.vBoxLayout.addLayout(self.hly_content)
        self.vBoxLayout.addLayout(self.hly_btn)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_ensure.clicked.connect(lambda: self.accept_status.emit(True))
        self.btn_cancel.clicked.connect(lambda: self.accept_status.emit(False))
