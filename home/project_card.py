from qfluentwidgets import ElevatedCardWidget, StrongBodyLabel, TitleLabel, BodyLabel
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout


class ProjectCard(ElevatedCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vly_1 = QVBoxLayout(self)
        self.lbl_project_name = TitleLabel("asdasdasda")
        self.lbl_project_id = StrongBodyLabel("accasca")
        self.lbl_project_description = BodyLabel("casacs")

        self.lbl_project_tag = BodyLabel("casacs")
        self.lbl_project_datatime = BodyLabel("casacs")
        self.hly_bottom = QHBoxLayout()
        self.hly_bottom.addWidget(self.lbl_project_tag)
        self.hly_bottom.addWidget(self.lbl_project_datatime)
        self.vly_1.addWidget(self.lbl_project_name)
        self.vly_1.addWidget(self.lbl_project_id)
        self.vly_1.addWidget(self.lbl_project_description)
        self.vly_1.addStretch(1)
        self.vly_1.addLayout(self.hly_bottom)
        self.setFixedSize(280, 240)
