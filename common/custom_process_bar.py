from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import ProgressBar, BodyLabel


class CustomProcessBar(QWidget):
    def __init__(self, parent=None):
        super(CustomProcessBar, self).__init__(parent=parent)
        self.value = 0
        self.max_value = 0

        self.psb_hly = QHBoxLayout(self)
        self.psb_train = ProgressBar()
        self.lbl_train_process = BodyLabel(f"{self.value:>3} / {self.max_value:<3}", self)
        self.psb_hly.addWidget(self.psb_train)
        self.psb_hly.addWidget(self.lbl_train_process)

    def set_value(self, value):
        self.value = value
        self.psb_train.setValue(value)
        self.lbl_train_process.setText(f"{self.value:>3} / {self.max_value:<3}")

    def set_max_value(self, max_value):
        self.max_value = max_value
        self.psb_train.setMaximum(max_value)
        self.lbl_train_process.setText(f"{self.value:>3} / {self.max_value:<3}")
