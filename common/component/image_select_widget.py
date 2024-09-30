from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QMouseEvent, QImage, QPen, QPainterPath, QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout
from qfluentwidgets import ImageLabel

from common.utils.utils import is_image


class ImageSelectWidget(QWidget):
    image_selected = Signal(str)

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

    def _scale_image(self):
        if self.width() > self.height():
            if self.lbl_image.image.width() > self.lbl_image.image.height():
                self.lbl_image.scaledToWidth(self.width() - 2)  # 减去线宽
            else:
                self.lbl_image.scaledToHeight(self.height() - 2)
        else:
            if self.lbl_image.image.width() > self.lbl_image.image.height():
                self.lbl_image.scaledToHeight(self.height() - 2)
            else:
                self.lbl_image.scaledToWidth(self.width() - 2)

    def set_image(self, image: str | QPixmap | QImage = None):
        """ set the image of label """
        self.lbl_image.setImage(image)
        self._scale_image()

    def setFixedSize(self, *args, **kwargs) -> None:
        super().setFixedSize(*args, **kwargs)
        self._scale_image()

    def set_border_radius(self, top_left: int, top_right: int, bottom_left: int, bottom_right: int):
        """ set the border radius of image """
        self._bottom_right_radius = top_left
        self._bottom_left_radius = top_right
        self._top_right_radius = bottom_left
        self._top_left_radius = bottom_right
        self.lbl_image.setBorderRadius(0, 0, 0, 0)
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
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.width() // 2 - 20, self.height() // 2, self.width() // 2 + 20, self.height() // 2)
        painter.drawLine(self.width() // 2, self.height() // 2 - 20, self.width() // 2, self.height() // 2 + 20)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)

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
        if filename and is_image(filename):
            self._cur_path = filename
            self._is_hovered = False
            self.set_image(self._cur_path)
            self.image_selected.emit(self._cur_path)
