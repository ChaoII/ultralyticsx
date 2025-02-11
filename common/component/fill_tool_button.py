from PySide6.QtCore import Signal, Qt, QRectF, QSize, QEvent
from PySide6.QtGui import QPainter, QColor, QEnterEvent, QMouseEvent, QBrush
from PySide6.QtWidgets import (QWidget)
from qfluentwidgets import themeColor
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
        self._border_radius = 4
        self._bg_color = themeColor()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._is_hover = False
        self._is_pressed = False

        cfg.themeChanged.connect(lambda: self.set_background_color(themeColor()))

    def set_icon(self, icon):
        self._icon = icon

    def set_border_radius(self, radius: int):
        self._border_radius = radius

    def set_icon_size(self, icon_size: QSize):
        self._icon_size = icon_size

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
        bg_color.setAlpha(40)
        rect = self.rect().adjusted(0, 0, -1, -1)
        icon_rect = QRectF(x, y, w, h).adjusted(0, 0, -1, -1)

        if self._is_hover:
            bg_color = self._bg_color.darker(150)
        if self._is_pressed:
            bg_color = self._bg_color.darker(200)
            # 点击时右下移动，有按下去的感觉
            rect = self.rect().adjusted(1, 1, 1, 1)
            icon_rect = QRectF(x, y, w, h).adjusted(1, 1, 1, 1)
        painter.setPen(QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, self._border_radius, self._border_radius)
        drawIcon(self._icon, painter, icon_rect)

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
