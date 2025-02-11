from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QListWidgetItem, QTableWidget, QSizePolicy
from qfluentwidgets import ColorPickerButton, BodyLabel, SimpleCardWidget, StrongBodyLabel, FluentIcon, \
    TransparentToolButton, PopupTeachingTip, TeachingTipTailPosition, MessageBoxBase, LineEdit

from common.component.custom_list_widget import CustomListWidget
from common.component.delete_ensure_widget import CustomFlyoutView
from common.component.fill_tool_button import FillToolButton
from common.core.window_manager import window_manager


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
    label_item_deleted = Signal(str)
    label_item_color_changed = Signal(str, QColor)

    def __init__(self, label: str, color: QColor, parent=None):
        super().__init__(parent=parent)
        self.hly = QHBoxLayout(self)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.cb_label_status = ColorPickerButton(color, "")
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
        self.cb_label_status.colorChanged.connect(self.on_color_changed)
        self.btn_delete.clicked.connect(self._on_delete_clicked)

    def on_color_changed(self, color: QColor):
        self.label_item_color_changed.emit(self.label, color)

    def _on_delete_clicked(self):
        self.view = CustomFlyoutView(
            content=self.tr("Are you sure to delete this label? the corresponding annotations will be deleted!"))
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
            self.label_item_deleted.emit(self.label)
        self.popup_tip.close()

    def get_label(self):
        return self.label


class LabelSettingsWidget(SimpleCardWidget):
    delete_label_clicked = Signal(str)
    add_label_clicked = Signal(str)
    label_item_color_changed = Signal(str, QColor)

    def __init__(self):
        super().__init__()
        self.setObjectName("labelsWidget")
        self.setMinimumHeight(200)
        self.lbl_title = StrongBodyLabel(text=self.tr("labels"))
        self.lbl_title.setFixedHeight(20)
        self.cus_add_label = TransparentToolButton(FluentIcon.ADD, self)
        self.cus_add_label.setFixedSize(20, 20)
        self.cus_add_label.setEnabled(False)

        self.list_widget = CustomListWidget()
        self.list_widget.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.list_widget.disable_hover_effect()
        self.list_widget.set_item_height(25)

        self.hly_lbl = QHBoxLayout()
        self.hly_lbl.addWidget(self.lbl_title)
        self.hly_lbl.addStretch(1)
        self.hly_lbl.addWidget(self.cus_add_label)
        self.vly_content = QVBoxLayout(self)
        self.vly_content.addLayout(self.hly_lbl)
        self.vly_content.addWidget(self.list_widget)
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

    def set_labels(self, labels_color: dict):
        self.clear()
        for label, color in labels_color.items():
            item = QListWidgetItem()
            self.list_widget.addItem(item)
            label_item = LabelSettingsListItemWidget(label, color)
            label_item.label_item_deleted.connect(self.on_delete_item)
            label_item.label_item_color_changed.connect(self.label_item_color_changed)
            self.list_widget.setItemWidget(item, label_item)

    def on_delete_item(self, label):
        self.delete_label_clicked.emit(label)

    def on_label_item_color_changed(self, label, color):
        self.label_item_color_changed.emit(label, color)
