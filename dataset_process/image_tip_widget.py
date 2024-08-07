from PySide6.QtCore import Slot, Qt, QSize, Signal, QPoint
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import (QVBoxLayout)
from qfluentwidgets import FluentIcon, ImageLabel, FlyoutViewBase, TransparentToolButton, Flyout, FlyoutAnimationType

from utils.utils import *


class CustomFlyoutView(FlyoutViewBase):
    closed = Signal()

    def __init__(self, lbl_image: ImageLabel, parent=None):
        super().__init__(parent)
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setSpacing(0)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_close = TransparentToolButton(FluentIcon.CLOSE, lbl_image)
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.clicked.connect(self._clicked_close)
        self.addWidget(lbl_image)

    def addWidget(self, widget: QWidget, stretch=0, align=Qt.AlignmentFlag.AlignLeft):
        self.widget_layout.addWidget(widget)

    @Slot()
    def _clicked_close(self):
        self.closed.emit()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.btn_close.move(self.width() - self.btn_close.width() - 10, 10)


class ImageTip(QWidget):
    def __init__(self, pix: QPixmap, target: QWidget | QPoint, max_side=300):
        super().__init__()

        self.lbl_image = ImageLabel()
        self.lbl_image.setPixmap(pix)
        self.lbl_image.setBorderRadius(8, 8, 8, 8)
        # 按比例缩放到指定高度
        self.lbl_image.scaledToHeight(max_side)
        self.target = QPoint(target.x() - self.lbl_image.width(), target.y() - self.lbl_image.height())
        self.view = CustomFlyoutView(self.lbl_image)
        self.view.closed.connect(self._close_tip)
        self.flyout = None

    @Slot()
    def _close_tip(self):
        self.flyout.close()

    def showFlyout(self):
        self.flyout = Flyout.make(self.view, self.target, self,
                                  aniType=FlyoutAnimationType.PULL_UP,
                                  isDeleteOnClose=True)
