from PySide6.QtCore import Qt, QRectF, QRect, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PySide6.QtWidgets import (QWidget)
from qfluentwidgets.common.icon import toQIcon, drawIcon, isDarkTheme


class TagWidget(QWidget):
    """ Scroll button """

    def __init__(self, icon, text=""):
        super().__init__()
        self._light_color = QColor(0, 0, 0)
        self._dark_color = QColor(255, 255, 255)
        self._icon = icon
        self._text = text
        self.setMinimumSize(120, 32)
        self._icon_size = QSize(0, 0)
        self.setIconSize(QSize(16, 16))
        self._fit_width()

    def set_icon(self, icon):
        self._icon = icon

    def _fit_width(self):
        # 获取字体大小
        font = QFont()
        fm = QFontMetrics(font)
        self.text_width = fm.boundingRect(self._text).width()
        # self.setFixedWidth(12 + 2 + self.text_width + self._icon_size.width() * 2)
        self.setFixedSize(QSize(100, 26))

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

    def set_color(self, light_color: QColor, dark_color: QColor):
        self._light_color = light_color
        self._dark_color = dark_color

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

        if isDarkTheme():
            color = self._dark_color
        else:
            color = self._light_color
        drawIcon(self._icon, painter, QRectF(x, y, w, h), fill=color.name())
        text_rect = QRect(self.rect().topLeft() + QPoint(x + self._icon_size.width(), 0),
                          self.rect().bottomRight() - QPoint(x, 0))
        painter.setPen(QPen(color, 2))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._text)
        brush_color = QColor(color.red(), color.green(), color.blue(), 100)
        painter.setBrush(brush_color)
        painter.drawRoundedRect(self.rect(), 10, 10)


class TextTagWidget(QWidget):
    """ Scroll button """

    def __init__(self, text="", light_color: QColor = QColor(0, 0, 0), dark_color: QColor = QColor(255, 255, 255)):
        super().__init__()
        self._dark_color = dark_color
        self._light_color = light_color
        self._text = text
        self.setMinimumSize(120, 32)
        self._fit_width()

    def _fit_width(self):
        # 获取字体大小
        font = QFont()
        fm = QFontMetrics(font)
        self.text_width = fm.boundingRect(self._text).width()
        # self.setFixedWidth(12 + 2 + self.text_width + self._icon_size.width() * 2)
        self.setFixedSize(QSize(100, 26))

    def text(self):
        return self._text

    def set_text(self, text):
        self._text = text
        self._fit_width()

    def set_color(self, light_color: QColor, dark_color: QColor):
        self._light_color = light_color
        self._dark_color = dark_color

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            pen_color = self._dark_color
        else:
            pen_color = self._light_color

        painter.setPen(QPen(pen_color, 2))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)
        brush_color = QColor(pen_color.red(), pen_color.green(), pen_color.blue(), 100)
        painter.setBrush(brush_color)
        painter.drawRoundedRect(self.rect(), 4, 4)
