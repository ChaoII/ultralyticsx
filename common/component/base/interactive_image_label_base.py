from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ImageLabel


class InteractiveImageLabelBase(QWidget):
    def __init__(self):
        super().__init__()
        self.lbl_image = ImageLabel()
        self._bottom_right_radius = 8
        self._bottom_left_radius = 8
        self._top_right_radius = 8
        self._top_left_radius = 8

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
        raise NotImplementedError

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
        painter.drawPath(path)
