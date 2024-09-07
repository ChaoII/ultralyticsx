from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QRect, QTimer, QObject
from PySide6.QtGui import QMouseEvent, QIcon, QPaintEvent, QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import TransparentToolButton, FluentIcon, SimpleCardWidget, StrongBodyLabel, BodyLabel, ComboBox
from typing_extensions import overload

from common.custom_icon import CustomFluentIcon
from common.custom_scroll_widget import CustomScrollWidget


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

    def set_title(self, title: str):
        self.header.setText(title)

    def set_icon(self, icon):
        self.btn_collapse.setIcon(icon)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.collapse_clicked.emit()


class CollapsibleWidgetItem(QWidget):
    collapse_clicked = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.header = HeaderWidget(title)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.setSpacing(9)
        self.vly_content.setContentsMargins(0, 0, 0, 0)
        self.vly_content.addWidget(self.header)
        self.content_widget: None | QWidget = None
        self._is_collapsed = False

        self.header.collapse_clicked.connect(self._on_collapse_clicked)

    def set_content_widget(self, widget: QWidget):
        if self.content_widget:
            self.vly_content.removeWidget(self.content_widget)
        self.content_widget = widget
        self.vly_content.addWidget(self.content_widget)

    def set_collapsed(self, collapsed: bool):
        self._is_collapsed = collapsed
        if self._is_collapsed:
            self.header.set_icon(CustomFluentIcon.UNFOLD)
        else:
            self.header.set_icon(CustomFluentIcon.FOLD)
        if not self.content_widget:
            return
        self.content_widget.setHidden(collapsed)

    @Slot()
    def _on_collapse_clicked(self):
        # 如果是折叠，那么展开\
        self.set_collapsed(not self._is_collapsed)
        self.collapse_clicked.emit()


class ToolBox(QWidget):
    current_index_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.setContentsMargins(0, 0, 0, 0)
        self.vly_content.setSpacing(0)
        self.vly_content.addStretch(1)
        self.scroll_area = CustomScrollWidget(orient=Qt.Orientation.Vertical)
        self.scroll_area.setLayout(self.vly_content)

        self.vly = QVBoxLayout(self)
        self.vly.addWidget(self.scroll_area)
        self._connect_signals_and_slots()
        self._current_index = -1
        self._items: list[CollapsibleWidgetItem] = []

    def add_item(self, item: CollapsibleWidgetItem):
        self.vly_content.insertWidget(self.count(), item)
        item.collapse_clicked.connect(self._on_current_item_clicked)
        self._items.append(item)
        if len(self._items) == 1:
            self.set_current_index(0)

    def count(self):
        return len(self._items)

    def current_index(self):
        return self._current_index

    def set_current_index(self, index: int):
        if not 0 <= index < len(self._items) or index == self.current_index():
            return
        self.collapse_all()
        self._items[index].set_collapsed(False)
        self._current_index = index
        self.current_index_changed.emit(index)

    def current_widget(self):
        return self._items[self._current_index]

    def index_of(self, item: CollapsibleWidgetItem):
        return self._items.index(item)

    def insert_item(self, index: int, item: CollapsibleWidgetItem):
        self._items.insert(index, item)

        if index <= self.current_index():
            self.set_current_index(self.current_index() + 1)

    def remove_item(self, index: int):
        if not 0 <= index < len(self._items):
            return
        self._items.pop(index)
        if index < self.current_index():
            self.set_current_index(self._current_index - 1)
        elif index == self.current_index():
            if index > 0:
                self.set_current_index(self._current_index - 1)
            else:
                self.current_index_changed.emit(0)

        if self.count() == 0:
            self.clear()

    def widget(self, index: int):
        if index < 0 or index > self.count():
            return
        return self._items[index]

    def clear(self):
        self._items.clear()
        self._current_index = -1

    def _connect_signals_and_slots(self):
        pass

    def _on_current_item_clicked(self):
        index = self.index_of(self.sender())
        self.set_current_index(index)

    def collapse_all(self):
        for item in self._items:
            item.set_collapsed(True)

    def expansion_all(self):
        for item in self._items:
            item.set_collapsed(False)
