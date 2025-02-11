from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QMouseEvent, QImage, QPen, QPixmap
from PySide6.QtWidgets import QFileDialog

from common.component.base.interactive_image_label_base import InteractiveImageLabelBase
from common.utils.utils import is_image


class ImageSelectWidget(InteractiveImageLabelBase):
    image_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self._cur_path = "."

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen()
        pen.setColor(Qt.GlobalColor.gray)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.width() // 2 - 20, self.height() // 2, self.width() // 2 + 20, self.height() // 2)
        painter.drawLine(self.width() // 2, self.height() // 2 - 20, self.width() // 2, self.height() // 2 + 20)

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
            self.set_image(self._cur_path)
            self.image_selected.emit(self._cur_path)

    def set_image(self, image: str | QPixmap | QImage = None):
        """ set the image of label """
        self.lbl_image.setImage(image)
        self._scale_image()
