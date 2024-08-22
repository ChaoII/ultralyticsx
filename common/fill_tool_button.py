from typing import Union

import overrides
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve, QRectF, QRect, QPoint, QSize, QEvent
from PySide6.QtGui import QPainter, QColor, QIcon, QPen, QFont, QFontMetrics, QEnterEvent, QMouseEvent, QBrush
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QLayout, QApplication, QAbstractButton, QToolButton)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme, PillPushButton, PipsPager, ToolButton, FluentIconBase, Icon, PrimaryToolButton, HyperlinkButton, \
    themeColor
from qfluentwidgets.common.icon import toQIcon, drawIcon
from settings import cfg


class FillToolButton(QWidget):
    """ Scroll button """
    clicked = Signal()

    def __init__(self, icon):
        super().__init__()
        self._icon_color = QColor(255, 0, 0)
        self._icon = icon
        self.setMinimumSize(24, 24)
        self._icon_size = QSize(16, 16)
        self._bg_color = themeColor()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._is_hover = False
        self._is_pressed = False

    def set_background_color(self, color: QColor):
        self._bg_color = color

    def background_color(self):
        return self._bg_color

    def iconSize(self) -> QSize:
        return self._icon_size

    def icon(self):
        return toQIcon(self._icon)

    def set_icon_color(self, color: QColor):
        self._icon_color = color

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.iconSize().width(), self.iconSize().height()
        x = (self.width() - w) // 2
        y = (self.height() - h) / 2

        bg_color = self._bg_color
        rect = self.rect().adjusted(0, 0, -1, -1)
        icon_rect = QRectF(x, y, w, h).adjusted(0, 0, -1, -1)

        if self._is_hover:
            bg_color = QColor(self._bg_color.red(), self._bg_color.green(), self._bg_color.blue(), 100)
        if self._is_pressed:
            bg_color = QColor(self._bg_color.red(), self._bg_color.green(), self._bg_color.blue(), 120)
            rect = self.rect().adjusted(1, 1, 1, 1)
            icon_rect = QRectF(x, y, w, h).adjusted(1, 1, 1, 1)

        painter.setPen(QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, 4, 4)
        drawIcon(self._icon, painter, icon_rect, fill=self._icon_color.name())

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self._is_hover = True
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self._is_hover = False
        self._is_pressed = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.clicked.emit()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self.update()
