from ctypes import Union
from pathlib import Path

from PySide6.QtCore import QSize, QRect, Qt, Signal
from PySide6.QtGui import QPainter, QMouseEvent, QFontMetrics, QImage, QPen, QPainterPath, QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import themeColor, LineEdit, ImageLabel
from qfluentwidgets.common.icon import toQIcon, drawIcon

from .custom_icon import CustomFluentIcon
from .utils import is_image


class ImageSelectWidget(QWidget):
    """ Scroll button """
    path_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self._bottom_right_radius = 8
        self._bottom_left_radius = 8
        self._top_right_radius = 8
        self._top_left_radius = 8
        self._is_hovered = False
        self._cur_path = ""
        self.image: QImage | None = None

    def set_image(self, image: str | QPixmap | QImage = None):
        """ set the image of label """
        self.image = image or QImage()
        if isinstance(image, str):
            self.image = QImage(image)
        elif isinstance(image, QPixmap):
            self.image = image.toImage()
        # self.setFixedSize(self.image.size())
        self.update()

    def set_border_radius(self, top_left: int, top_right: int, bottom_left: int, bottom_right: int):
        """ set the border radius of image """
        self._bottom_right_radius = top_left
        self._bottom_left_radius = top_right
        self._top_right_radius = bottom_left
        self._top_left_radius = bottom_right
        self.update()

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

        if not self.image:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.gray)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.width() // 2 - 20, self.height() // 2, self.width() // 2 + 20, self.height() // 2)
            painter.drawLine(self.width() // 2, self.height() // 2 - 20, self.width() // 2, self.height() // 2 + 20)
            painter.drawPath(path)
        else:
            image = self.image.scaled(
                self.size() * self.devicePixelRatioF(), Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setClipPath(path)
            painter.drawImage(self.rect(), image)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_hovered = True

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._is_hovered = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self._open_directory()

    def _open_directory(self):
        if Path(self._cur_path).exists():
            if Path(self._cur_path).is_file():
                _dir = Path(self._cur_path).parent.resolve().as_posix()
            else:
                _dir = Path.home().as_posix()
        else:
            _dir = Path.home().as_posix()
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("Select a file"), _dir)
        if is_image(filename):
            self._cur_path = filename
            self._is_hovered = False
            self.set_image(self._cur_path)


class ImageSelectWidget1(QWidget):
    """ Scroll button """
    path_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.image_label = ImageLabel()

    def set_image(self, image: str | QPixmap | QImage = None):
        """ set the image of label """
        self.image = image or QImage()
        if isinstance(image, str):
            self.image = QImage(image)
        elif isinstance(image, QPixmap):
            self.image = image.toImage()
        # self.setFixedSize(self.image.size())
        self.update()

    def set_border_radius(self, top_left: int, top_right: int, bottom_left: int, bottom_right: int):
        """ set the border radius of image """
        self._bottom_right_radius = top_left
        self._bottom_left_radius = top_right
        self._top_right_radius = bottom_left
        self._top_left_radius = bottom_right
        self.update()

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

        if not self.image:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.gray)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.width() // 2 - 20, self.height() // 2, self.width() // 2 + 20, self.height() // 2)
            painter.drawLine(self.width() // 2, self.height() // 2 - 20, self.width() // 2, self.height() // 2 + 20)
            painter.drawPath(path)
        else:
            image = self.image.scaled(
                self.size() * self.devicePixelRatioF(), Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setClipPath(path)
            painter.drawImage(self.rect(), image)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_hovered = True

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._is_hovered = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self._open_directory()

    def _open_directory(self):
        if Path(self._cur_path).exists():
            if Path(self._cur_path).is_file():
                _dir = Path(self._cur_path).parent.resolve().as_posix()
            else:
                _dir = Path.home().as_posix()
        else:
            _dir = Path.home().as_posix()
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("Select a file"), _dir)
        if is_image(filename):
            self._cur_path = filename
            self._is_hovered = False
            self.set_image(self._cur_path)
