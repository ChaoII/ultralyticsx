from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import ProgressBar, CaptionLabel


class CustomProcessBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.psb_hly = QHBoxLayout(self)
        self.label_hly = QHBoxLayout()
        self.label_hly.setContentsMargins(0, 0, 0, 0)
        self.psb_train = ProgressBar()
        self.lbl_value = CaptionLabel("", self)
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_value.setMinimumWidth(20)
        self.lbl_split = CaptionLabel("/", self)
        self.lbl_total = CaptionLabel("", self)
        self.lbl_total.setMinimumWidth(20)
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_hly.addWidget(self.lbl_value)
        self.label_hly.addWidget(self.lbl_split)
        self.label_hly.addWidget(self.lbl_total)
        self.psb_hly.addWidget(self.psb_train)
        self.psb_hly.addLayout(self.label_hly)
        self.setMinimumWidth(200)

    def set_text_visible(self, visible: bool) -> None:
        self.lbl_value.setVisible(visible)
        self.lbl_split.setVisible(visible)
        self.lbl_total.setVisible(visible)

    def set_value(self, value):
        self.psb_train.setValue(value)
        self.lbl_value.setText(str(value))

    def set_max_value(self, max_value):
        self.psb_train.setMaximum(max_value)
        self.lbl_total.setText(str(max_value))

    def set_error(self, is_error):
        self.psb_train.setError(is_error)

    def set_pause(self, is_paused):
        self.psb_train.setPaused(is_paused)

    def resume(self):
        self.psb_train.resume()
