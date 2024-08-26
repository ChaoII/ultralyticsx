from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSizeGrip, QHBoxLayout, \
    QGraphicsOpacityEffect, QGroupBox
from PySide6.QtCore import QPropertyAnimation, QRect, Qt, QEasingCurve, Property, QSize, Signal
from PySide6.QtGui import QResizeEvent, QPaintEvent, QPainter, QMouseEvent
from qfluentwidgets import SubtitleLabel, TransparentToolButton, FluentIcon, PushButton, ElevatedCardWidget, \
    SimpleCardWidget, StrongBodyLabel

from common.custom_scroll_widget import   CustomScrollWidget


class HeaderWidget(SimpleCardWidget):
    collapse_clicked = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header = StrongBodyLabel(title, self)
        self.btn_collapse = TransparentToolButton(FluentIcon.CHEVRON_DOWN_MED, self)
        self.btn_collapse.setEnabled(False)

        self.hly_header = QHBoxLayout(self)
        self.hly_header.addWidget(self.header)
        self.hly_header.addStretch(1)
        self.hly_header.addWidget(self.btn_collapse)

    def setIcon(self, icon):
        self.btn_collapse.setIcon(icon)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.collapse_clicked.emit()


class CollapsibleWidget(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.header = HeaderWidget(title)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.setSpacing(0)
        self.vly_content.setContentsMargins(0, 0, 0, 0)
        self.vly_content.addWidget(self.header)
        self.content_widget = None

        self._is_collapsed = True
        self._connect_signals_and_slots()

    def set_content_widget(self, widget: QWidget):
        if self.content_widget:
            self.content_widget = None
        self.content_widget = widget
        self.content_widget.setHidden(True)
        self.vly_content.addWidget(self.content_widget)

    def set_content_hidden(self, hidden: bool):
        self._is_collapsed = hidden
        if not self.content_widget:
            return
        self.content_widget.setHidden(hidden)

    def _connect_signals_and_slots(self):
        self.header.collapse_clicked.connect(self._on_collapse_clicked)

    def _on_collapse_clicked(self):
        # 如果是折叠，那么展开
        print(self._is_collapsed)
        if self._is_collapsed:
            self.header.setIcon(FluentIcon.UP)
        else:
            self.header.setIcon(FluentIcon.CHEVRON_DOWN_MED)
        self.set_content_hidden(not self._is_collapsed)
