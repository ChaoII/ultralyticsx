import overrides
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QLayout)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme, PillPushButton, PipsPager, ToolButton, FluentIconBase, Icon

from settings import cfg


def drawIcon(icon, painter, rect, state=QIcon.State.Off, **attributes):
    """ draw icon

    Parameters
    ----------
    icon: str | QIcon | FluentIconBaseBase
        the icon to be drawn

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon

    **attribute:
        the attribute of svg icon
    """
    if isinstance(icon, FluentIconBase):
        icon.render(painter, rect, **attributes)
    elif isinstance(icon, Icon):
        icon.fluentIcon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        icon.paint(painter, QRectF(rect).toRect(), Qt.AlignmentFlag.AlignCenter, state=state)


class ScrollButton(ToolButton):
    """ Scroll button """

    def _postInit(self):
        self.setFixedSize(12, 12)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if isDarkTheme():
            color = QColor(255, 255, 255)
            painter.setOpacity(0.773 if self.isHover or self.isPressed else 0.541)
        else:
            color = QColor(0, 0, 0)
            painter.setOpacity(0.616 if self.isHover or self.isPressed else 0.45)

        if self.isPressed:
            rect = QRectF(3, 3, 6, 6)
        else:
            rect = QRectF(2, 2, 8, 8)

        drawIcon(self._icon, painter, rect, fill=color.name())


class CustomScrollWidget(SingleDirectionScrollArea):
    pass
