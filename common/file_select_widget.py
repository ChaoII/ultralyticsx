from qfluentwidgets import ElevatedCardWidget, BodyLabel, Dialog, MessageBoxBase, FluentStyleSheet, PrimaryPushButton, \
    TextWrap, LineEdit, TextEdit, PrimaryToolButton, FluentIcon, SearchLineEdit, FluentIconBase
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QWidget
from qframelesswindow import FramelessDialog
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QToolButton, QFileDialog, QSizePolicy
from PySide6.QtCore import Signal, Qt, QSize, QRectF, Slot
from PySide6.QtGui import QPainter, QIcon
from pathlib import Path


class DirSelectWidget(QWidget):
    """ Search line edit """

    dir_selected = Signal(str)
    clearSignal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.le_dir = LineEdit()
        self.btn_open_dir = PrimaryToolButton(FluentIcon.FOLDER, self)
        self.hly_content = QHBoxLayout(self)
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.hly_content.setSpacing(0)
        self.hly_content.addWidget(self.le_dir)
        self.hly_content.addWidget(self.btn_open_dir)
        self.btn_open_dir.clicked.connect(self._on_clicked)

    @Slot()
    def _on_clicked(self):
        dir_name = QFileDialog.getExistingDirectory(self, self.tr("info"), ".")
        if dir_name:
            dir_name_normal = Path(dir_name).resolve().as_posix()
            self.le_dir.setText(dir_name_normal)
            self.dir_selected.emit(dir_name_normal)
