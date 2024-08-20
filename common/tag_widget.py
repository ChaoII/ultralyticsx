from typing import Union

import overrides
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve, QRectF, QRect, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QIcon, QPen, QFont, QFontMetrics
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QLayout, QApplication, QAbstractButton)
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


class TagWidget(QWidget):
    """ Scroll button """

    def __init__(self, icon, text=""):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._icon = icon
        self._text = text
        self.setMinimumSize(120, 32)
        self._icon_size = QSize(0, 0)
        self.setIconSize(QSize(16, 16))
        self._fit_width()

    def _fit_width(self):
        # 获取字体大小
        font = QFont()
        fm = QFontMetrics(font)
        self.text_width = fm.boundingRect(self._text).width()
        # self.setFixedWidth(12 + 2 + self.text_width + self._icon_size.width() * 2)
        self.setFixedWidth(100)

    def setIconSize(self, size: QSize):
        self._icon_size = size
        self._fit_width()

    def setText(self, text):
        self._text = text
        self._fit_width()

    def iconSize(self) -> QSize:
        return self._icon_size

    def icon(self):
        return toQIcon(self._icon)

    def set_color(self, color: QColor):
        self._color = color
        # self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.icon().isNull() and self._text is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        gap = 8  # 文字和icon之间的间隔
        x = (self.width() - self._icon_size.width() - self.text_width) // 2 - gap

        if self.isRightToLeft():
            x = self.width() - w - x
        drawIcon(self._icon, painter, QRectF(x, y, w, h), fill=self._color.name())
        text_rect = QRect(self.rect().topLeft() + QPoint(x + self._icon_size.width(), 0),
                          self.rect().bottomRight() - QPoint(x, 0))
        painter.setPen(QPen(self._color, 2))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._text)
        brush_color = QColor(self._color.red(), self._color.green(), self._color.blue(), 100)
        painter.setBrush(brush_color)
        painter.drawRoundedRect(self.rect(), 10, 10)
