from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QButtonGroup, QVBoxLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, RadioButton, CheckBox, ProgressRing, \
    FluentStyleSheet, isDarkTheme, IndeterminateProgressRing
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase

from settings import cfg


class MessageBoxBaseTransparent(MaskDialogBase):
    """ Message box base """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vBoxLayout = QVBoxLayout(self.widget)
        self.viewLayout = QVBoxLayout()
        self.__initWidget()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

    def __initWidget(self):
        self.__setQss()
        self.__initLayout()

        if isDarkTheme():
            self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
            self.setMaskColor(QColor(0, 0, 0, 200))
        else:
            self.setShadowEffect(60, (0, 10), QColor(255, 255, 255, 50))
            self.setMaskColor(QColor(255, 255, 255, 200))

    def __initLayout(self):
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignmentFlag.AlignCenter)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.viewLayout, 1)

        self.viewLayout.setSpacing(12)
        self.viewLayout.setContentsMargins(24, 24, 24, 24)

    def __setQss(self):
        FluentStyleSheet.DIALOG.apply(self)


class ProgressMessageBox(MessageBoxBaseTransparent):
    """ Custom message box """

    def __init__(self, indeterminate=False, parent=None):
        super().__init__(parent)
        self._indeterminate = indeterminate
        if indeterminate:
            self.pgr = IndeterminateProgressRing()
        else:
            self.pgr = ProgressRing()
            self.pgr.setTextVisible(True)
            self.pgr.setFormat(f"{self.tr('current progress: ')}%p%")
        self.pgr.setFixedSize(300, 300)
        self.pgr.setStrokeWidth(15)
        # 将组件添加到布局中
        self.viewLayout.addWidget(self.pgr)

    def set_error(self, is_error: bool):
        if not self._indeterminate:
            self.pgr.setError(is_error)

    def set_stroke_width(self, width: int):
        self.pgr.setStrokeWidth(width)

    def set_ring_size(self, width, height):
        self.pgr.setFixedSize(width, height)

    def set_paused(self, is_paused: bool):
        if not self._indeterminate:
            self.pgr.setPaused(is_paused)

    def set_max_value(self, value):
        if not self._indeterminate:
            self.pgr.setMaximum(value)

    def set_value(self, value):
        if not self._indeterminate:
            self.pgr.setValue(value)
