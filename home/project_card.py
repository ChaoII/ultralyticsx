from qfluentwidgets import ElevatedCardWidget, BodyLabel
from PySide6.QtWidgets import QVBoxLayout


class ProjectCard(ElevatedCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vly_1 = QVBoxLayout(self)
        self.lbl_project_name = BodyLabel("asdasdasda")
        self.lbl_project_id = BodyLabel("accasca")
        self.lbl_project_description = BodyLabel("casacs")
        self.lbl_project_tag = BodyLabel("casacs")
        self.lbl_project_datatime = BodyLabel("casacs")
        self.vly_1.addWidget(self.lbl_project_name)
        self.vly_1.addWidget(self.lbl_project_id)
        self.vly_1.addWidget(self.lbl_project_description)
        self.vly_1.addWidget(self.lbl_project_description)
        self.vly_1.addWidget(self.lbl_project_description)
        self.setFixedSize(320, 280)
