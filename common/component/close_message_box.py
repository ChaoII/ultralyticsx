from PySide6.QtWidgets import QButtonGroup
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, RadioButton, CheckBox

from settings import cfg


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = SubtitleLabel(self.tr("Information"), self)
        self.cb_remember_minimize_to_tray = CheckBox(self.tr("No longer show"), self)
        self.cb_remember_minimize_to_tray.setFixedWidth(400)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.cb_remember_minimize_to_tray)

        self.yesButton.setText(self.tr("Quit directly"))
        self.cancelButton.setText(self.tr("Minimize to tray"))
        self.buttonLayout.insertStretch(0, 1)
        self.is_accept = False
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.yesButton.clicked.connect(self._on_yes_button_clicked)
        self.cancelButton.clicked.connect(self._on_cancel_button_clicked)

    def _on_yes_button_clicked(self):
        self.remember_minimize_to_tray()
        self.is_accept = True
        self.accept()

    def _on_cancel_button_clicked(self):
        self.remember_minimize_to_tray()
        self.is_accept = False
        self.reject()

    def get_accept_status(self) -> bool:
        return self.is_accept

    def remember_minimize_to_tray(self):
        status = self.cb_remember_minimize_to_tray.isChecked()
        cfg.set(cfg.remember_quit_status, status)
