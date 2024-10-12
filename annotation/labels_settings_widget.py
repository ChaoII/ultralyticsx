from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QFormLayout
from qfluentwidgets import ColorPickerButton, BodyLabel, SimpleCardWidget, StrongBodyLabel

from common.component.custom_scroll_widget import CustomScrollWidget
from common.utils.utils import generate_random_color


class LabelSettingsWidget(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("labelsWidget")
        self.setFixedWidth(200)
        self.setMinimumHeight(200)
        self.lbl_title = StrongBodyLabel(text=self.tr("labels"))
        self.vly_labels = QVBoxLayout()
        self.vly_content = QVBoxLayout(self)
        self.vly_content.addWidget(self.lbl_title)
        self.scroll_area = CustomScrollWidget(orient=Qt.Orientation.Vertical)
        self.scroll_area.setLayout(self.vly_labels)
        self.vly_content.addWidget(self.scroll_area)

    def set_labels(self, labels: list[str]):
        for label in labels:
            fly = QFormLayout()
            fly.setSpacing(20)
            fly.setContentsMargins(0, 0, 0, 0)
            color_picker_btn = ColorPickerButton(generate_random_color(), "")
            color_picker_btn.setFixedSize(24, 24)
            fly.addRow(color_picker_btn, BodyLabel(text=label))
            self.vly_labels.addLayout(fly)
        self.vly_labels.addStretch(1)
