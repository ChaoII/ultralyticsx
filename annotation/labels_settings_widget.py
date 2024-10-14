from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QWidget, QHBoxLayout, QListWidgetItem, QTableWidget
from qfluentwidgets import ColorPickerButton, BodyLabel, SimpleCardWidget, StrongBodyLabel, ListWidget, FluentIcon, \
    TransparentToolButton, PopupTeachingTip, TeachingTipTailPosition, MessageBoxBase, LineEdit

from common.component.custom_icon import CustomFluentIcon
from common.component.custom_scroll_widget import CustomScrollWidget
from common.component.delete_ensure_widget import CustomFlyoutView
from common.component.fill_tool_button import FillToolButton
from common.core.window_manager import window_manager
from common.utils.utils import generate_random_color


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = StrongBodyLabel(self.tr("Add label"), self)
        self.le_label = LineEdit()

        self.le_label.setPlaceholderText(self.tr("Please input a new label"))
        self.le_label.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.le_label)
        self.widget.setFixedSize(300, 200)


class LabelSettingsListItemWidget(QWidget):
    item_deleted = Signal(str)

    def __init__(self, label: str, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = ColorPickerButton(generate_random_color(), "")
        self.cb_label_status.setFixedSize(16, 16)
        self.hly.addWidget(self.cb_label_status)
        self.hly.addWidget(BodyLabel(text=label))
        self.hly.addStretch(1)
        self.btn_delete = FillToolButton(FluentIcon.DELETE.icon(color=QColor("#E61919")))
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.set_icon_size(QSize(16, 16))
        self.hly.addWidget(self.btn_delete)
        self.label = label
        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self.btn_delete.clicked.connect(self._on_delete_clicked)

    def set_label_status(self, labeled=False):
        self.cb_label_status.setColor(Qt.GlobalColor.green if labeled else Qt.GlobalColor.red)

    def _on_delete_clicked(self):
        self.view = CustomFlyoutView(content=self.tr("Are you sure to delete this label?"))
        self.popup_tip = PopupTeachingTip.make(
            target=self.btn_delete,
            view=self.view,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=-1,
            parent=self
        )
        self.view.accept_status.connect(self.on_ensure_delete_item)

    def on_ensure_delete_item(self, accepted):
        if accepted:
            self.item_deleted.emit(self.label)
        self.popup_tip.close()


class LabelSettingsWidget(SimpleCardWidget):
    delete_label_clicked = Signal(str)
    add_label_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("labelsWidget")
        self.setFixedWidth(200)
        self.setMinimumHeight(200)

        self.lbl_title = StrongBodyLabel(text=self.tr("labels"))
        self.lbl_title.setFixedHeight(20)
        self.cus_add_label = TransparentToolButton(FluentIcon.ADD, self)
        self.cus_add_label.setFixedSize(20, 20)

        self.list_widget = ListWidget()
        self.list_widget.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        self.hly_lbl = QHBoxLayout()
        self.hly_lbl.addWidget(self.lbl_title)
        self.hly_lbl.addStretch(1)
        self.hly_lbl.addWidget(self.cus_add_label)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.addLayout(self.hly_lbl)
        self.vly_content.addWidget(self.list_widget)

        self.labels = []

        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self.cus_add_label.clicked.connect(self.on_add_label_clicked)

    def on_add_label_clicked(self):
        cus_message_box = CustomMessageBox(parent=window_manager.find_window("main_widget"))
        if cus_message_box.exec():
            label = cus_message_box.le_label.text()
            self.add_label_clicked.emit(label)

    def clear(self):
        self.list_widget.clear()

    def set_labels(self, labels: list[str]):
        self.labels = labels
        self.clear()
        for label in labels:
            item = QListWidgetItem()
            item.setSizeHint(QSize(item.sizeHint().width(), 100))
            self.list_widget.addItem(item)
            label_item = LabelSettingsListItemWidget(label)
            label_item.item_deleted.connect(self.on_delete_item)
            self.list_widget.setItemWidget(item, label_item)

    def on_delete_item(self, label):
        self.delete_label_clicked.emit(label)
