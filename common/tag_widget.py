import overrides
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QLayout)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme, PillPushButton, PipsPager, ToolButton, FluentIconBase, Icon, PrimaryToolButton, HyperlinkButton
from settings import cfg


def drawIcon(icon, painter, rect, state=QIcon.State.Off, **attributes):
    if isinstance(icon, FluentIconBase):
        icon.render(painter, rect, **attributes)
    elif isinstance(icon, Icon):
        icon.fluentIcon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        icon.paint(painter, QRectF(rect).toRect(), Qt.AlignmentFlag.AlignCenter, state=state)


class TagWidget(PushButton):
    """ Scroll button """

    # def __init__(self, color):
    #     super().__init__()
    #     self.setText("21312312")

    # def _postInit(self):
    #     self.setFixedSize(24, 24)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.icon().isNull():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if not self.isEnabled():
            painter.setOpacity(0.3628)
        elif self.isPressed:
            painter.setOpacity(0.786)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        mw = self.minimumSizeHint().width()
        if mw > 0:
            x = 12 + (self.width() - mw) // 2
        else:
            x = 12

        if self.isRightToLeft():
            x = self.width() - w - x

        drawIcon(self._icon, painter, QRectF(x, y, w, h), color=QColor(255, 0, 0).name())
