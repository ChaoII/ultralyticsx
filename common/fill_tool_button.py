from typing import Union

import overrides
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve, QRectF, QRect, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QIcon, QPen, QFont, QFontMetrics
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QLayout, QApplication, QAbstractButton, QToolButton)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme, PillPushButton, PipsPager, ToolButton, FluentIconBase, Icon, PrimaryToolButton, HyperlinkButton
from qfluentwidgets.common.icon import toQIcon
from settings import cfg


def drawIcon(icon, painter, rect, state=QIcon.State.Off, **attributes):
    if isinstance(icon, FluentIconBase):
        icon.render(painter, rect, **attributes)
    elif isinstance(icon, Icon):
        icon.fluentIcon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        icon.paint(painter, QRectF(rect).toRect(), Qt.AlignmentFlag.AlignCenter, state=state)


class FillToolButton(QToolButton):
    """ Scroll button """

    def __init__(self, icon):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._icon = icon
        self._icon_size = QSize(0, 0)
        self.setIconSize(QSize(16, 16))

    def icon(self):
        return toQIcon(self._icon)

    def set_icon(self, icon):
        self._icon = icon

    def set_color(self, color: QColor):
        self._color = color

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.icon().isNull():
            return
        painter = QPainter(self)
        painter.setPen(QPen(self._color, 1))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.iconSize().width(), self.iconSize().height()
        drawIcon(self._icon, painter, QRectF(0, 0, w, h), fill=self._color.name())
