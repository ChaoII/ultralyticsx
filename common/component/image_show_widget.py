from pathlib import Path

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QPainter, QImage, QPen, QPainterPath, QPixmap, QResizeEvent, QMouseEvent, QEnterEvent, QCursor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QFileDialog
from qfluentwidgets import ImageLabel, TransparentToolButton, FluentIcon, ToolButton

from .base.interactive_image_label_base import InteractiveImageLabelBase
from .custom_icon import CustomFluentIcon
from .image_tip_widget import ImageTip


class ImageShowWidget(InteractiveImageLabelBase):
    compact_mode_clicked = Signal(bool)

    def __init__(self):
        super().__init__()
        self.tb_down_load = TransparentToolButton(FluentIcon.DOWNLOAD, self)
        self.tb_down_load.setFixedSize(30, 30)
        self.tb_down_load.setVisible(False)
        self.tb_down_load.setToolTip(self.tr("Download image"))
        self.tb_down_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tb_compact = TransparentToolButton(CustomFluentIcon.COMPACT, self)
        self.tb_compact.setFixedSize(30, 30)
        self.tb_compact.setCheckable(True)
        self.tb_compact.setChecked(False)
        self.tb_compact.setVisible(False)
        self.tb_compact.setToolTip(self.tr("Compact mode"))
        self.tb_compact.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tb_maximum = TransparentToolButton(CustomFluentIcon.SHOW, self)
        self.tb_maximum.setFixedSize(30, 30)
        self.tb_maximum.setVisible(False)
        self.tb_maximum.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tb_maximum.setToolTip(self.tr("View"))
        self.connect_signals_and_slots()

        self.cur_dir = "."
        self.image_tip = None

    def connect_signals_and_slots(self):
        self.tb_maximum.clicked.connect(self.on_maximum_clicked)
        self.tb_compact.clicked.connect(self.on_compact_clicked)
        self.tb_down_load.clicked.connect(self.on_download_clicked)

    def on_maximum_clicked(self):
        if self.image:
            pix = QPixmap.fromImage(self.image)
            self.image_tip = ImageTip(pix, QCursor.pos())
            self.image_tip.showFlyout()

    def on_compact_clicked(self, checked: bool):
        if checked:
            self.tb_compact.setIcon(CustomFluentIcon.RELAX)
            self.tb_compact.setToolTip(self.tr("Relax mode"))
        else:
            self.tb_compact.setIcon(CustomFluentIcon.COMPACT)
            self.tb_compact.setToolTip(self.tr("Compact mode"))
        if self.image:
            self.compact_mode_clicked.emit(checked)

    def on_download_clicked(self):
        if not self.image:
            return
        default_filename = (Path(self.cur_dir) / "result.jpg").resolve().as_posix()
        filename, _ = QFileDialog.getSaveFileName(self, self.tr("Save Image"), default_filename,
                                                  "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.image.save(filename)
            self.cur_dir = Path(filename).parent.resolve().as_posix()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._scale_image()
        self.tb_down_load.move(self.width() - 35, 1)
        self.tb_compact.move(self.width() - 65, 1)
        self.tb_maximum.move(self.width() - 95, 1)
        self.lbl_image.move((self.width() - self.lbl_image.width()) // 2,
                            (self.height() - self.lbl_image.height()) // 2)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.tb_down_load.setVisible(True)
        self.tb_compact.setVisible(True)
        self.tb_maximum.setVisible(True)

    def leaveEvent(self, event: QEvent) -> None:
        self.tb_down_load.setVisible(False)
        self.tb_compact.setVisible(False)
        self.tb_maximum.setVisible(False)

    def set_image(self, image: str | QPixmap | QImage = None):
        """ set the image of label """
        self.image = image
        self.lbl_image.setImage(image)
        self._scale_image()
        self.lbl_image.move((self.width() - self.lbl_image.width()) // 2,
                            (self.height() - self.lbl_image.height()) // 2)
