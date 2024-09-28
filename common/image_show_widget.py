from ctypes import Union
from pathlib import Path

from PySide6.QtCore import QSize, QRect, Qt, Signal
from PySide6.QtGui import QPainter, QMouseEvent, QFontMetrics, QImage, QPen, QPainterPath, QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout
from qfluentwidgets import themeColor, LineEdit, ImageLabel
from qfluentwidgets.common.icon import toQIcon, drawIcon

from .custom_icon import CustomFluentIcon
from .utils import is_image


class ImageShowWidget(QWidget):
    path_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.lbl_image = ImageLabel()
        self._bottom_right_radius = 8
        self._bottom_left_radius = 8
        self._top_right_radius = 8
        self._top_left_radius = 8
        self._is_hovered = False
        self._cur_path = ""
        self.image: QImage | None = None
        self.vly_image = QVBoxLayout(self)
        self.vly_image.setContentsMargins(0, 0, 0, 0)
        self.vly_image.addWidget(self.lbl_image, 0, Qt.AlignmentFlag.AlignCenter)

    def set_image(self, image: str | QPixmap | QImage = None):
        """ set the image of label """
        self.lbl_image.setImage(image)
        self.lbl_image.scaledToWidth(self.width())

    def set_border_radius(self, top_left: int, top_right: int, bottom_left: int, bottom_right: int):
        """ set the border radius of image """
        self._bottom_right_radius = top_left
        self._bottom_left_radius = top_right
        self._top_right_radius = bottom_left
        self._top_left_radius = bottom_right
        self.lbl_image.setBorderRadius(top_left, top_right, bottom_left, bottom_right)
        self.update()

    def clear(self):
        self.set_image(QImage())

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        w, h = self.width(), self.height()
        # top line
        path.moveTo(self._top_left_radius, 0)
        path.lineTo(w - self._top_right_radius, 0)
        # top right arc
        d = self._top_right_radius * 2
        path.arcTo(w - d, 0, d, d, 90, -90)
        # right line
        path.lineTo(w, h - self._bottom_right_radius)
        # bottom right arc
        d = self._bottom_right_radius * 2
        path.arcTo(w - d, h - d, d, d, 0, -90)
        # bottom line
        path.lineTo(self._bottom_left_radius, h)
        # bottom left arc
        d = self._bottom_left_radius * 2
        path.arcTo(0, h - d, d, d, -90, -90)
        # left line
        path.lineTo(0, self._top_left_radius)
        # top left arc
        d = self._top_left_radius * 2
        path.arcTo(0, 0, d, d, -180, -90)

        # if not self.image:
        pen = QPen()
        pen.setColor(Qt.GlobalColor.gray)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)
