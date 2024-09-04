from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TransparentToolButton, FluentIcon, SimpleCardWidget, StrongBodyLabel,BodyLabel
from common.custom_icon import CustomFluentIcon


class HeaderWidget(SimpleCardWidget):
    collapse_clicked = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header = StrongBodyLabel(title, self)
        self.btn_collapse = TransparentToolButton(CustomFluentIcon.UNFOLD, self)
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
    collapse_clicked = Signal()

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
            self.vly_content.removeWidget(self.content_widget)
        self.content_widget = widget
        self.content_widget.setHidden(True)
        self.vly_content.addWidget(self.content_widget)

    def set_collapsed(self, collapsed: bool):
        self._is_collapsed = collapsed
        if self._is_collapsed:
            self.header.setIcon(CustomFluentIcon.UNFOLD)
        else:
            self.header.setIcon(CustomFluentIcon.FOLD)
        if not self.content_widget:
            return
        self.content_widget.setHidden(collapsed)

    def _connect_signals_and_slots(self):
        self.header.collapse_clicked.connect(self._on_collapse_clicked)

    def _on_collapse_clicked(self):
        # 如果是折叠，那么展开
        self.set_collapsed(not self._is_collapsed)
        self.collapse_clicked.emit()
