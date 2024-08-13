from qframelesswindow import FramelessWindow
from qfluentwidgets import themeColor
from PySide6.QtGui import QPaintEvent, QPainter, QPolygon, QPen, QFont, QFontMetrics
from PySide6.QtCore import Qt, QPoint, QRect

from utils.utils import invert_color


class ProjectTypeWidget(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 100)
        self.titleBar.setVisible(False)

    def paintEvent(self, event: QPaintEvent) -> None:
        super(ProjectTypeWidget, self).paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制自定义边框
        pen = QPen(themeColor(), 1)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        # 绘制右下角的三角形
        triangle = QPolygon([
            QPoint(self.width(), self.height()),
            QPoint(self.width() - int(self.width() / 4), self.height()),
            QPoint(self.width(), self.height() - int(self.height() / 4))
        ])

        triangle_pen = QPen(themeColor(), 2)
        painter.setPen(triangle_pen)
        painter.setBrush(themeColor())
        painter.setBrush(themeColor())
        painter.drawPolygon(triangle)

        # font_size = min(width_, height_) // 10  # 假设文字大小是窗口大小的10%
        font = QFont("Microsoft YaHei UI")
        font.setPixelSize(20)
        fm = QFontMetrics(font)
        label = "√"

        # 文字填充色
        new_rect = QRect(self.width() - 20, self.height() - fm.height(), fm.boundingRect("√").width(),
                         fm.height())

        painter.setFont(font)
        painter.setPen(QPen(invert_color(themeColor())))
        painter.drawText(new_rect, label)
