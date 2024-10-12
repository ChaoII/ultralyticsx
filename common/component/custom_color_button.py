from PySide6.QtGui import QColor, Qt, QPainter
from PySide6.QtWidgets import QToolButton
from blinker import Signal
from qfluentwidgets import ColorDialog, isDarkTheme


class CustomColorButton(QToolButton):

    def __init__(self, color: QColor, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(24, 24)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.color = color
        self.border_radius = 5
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def setColor(self, color):
        """ set color """
        self.color = color
        self.update()

    def set_border_radius(self, radius: int):
        self.border_radius = radius

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        pc = QColor(255, 255, 255, 10) if isDarkTheme() else QColor(234, 234, 234)
        painter.setPen(pc)
        painter.setBrush(self.color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), self.border_radius, self.border_radius)
