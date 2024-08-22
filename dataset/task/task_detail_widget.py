from PySide6.QtWidgets import QWidget
from qfluentwidgets import BodyLabel, ComboBox


class TaskDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("task_detail")
        self.lbl_select_dataset = BodyLabel(self.tr("Select dataset: "), self)
        self.cmb_select_dataset = ComboBox()
