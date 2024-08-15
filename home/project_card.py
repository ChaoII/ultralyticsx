from qfluentwidgets import ElevatedCardWidget, StrongBodyLabel, TitleLabel, BodyLabel
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout

from home.new_project import ProjectInfo


class ProjectCard(ElevatedCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vly_1 = QVBoxLayout(self)
        self.lbl_project_name = TitleLabel()
        self.lbl_project_id = StrongBodyLabel()
        self.lbl_project_description = BodyLabel()
        self.lbl_project_type = BodyLabel()
        self.lbl_create_time = BodyLabel()
        self.hly_bottom = QHBoxLayout()
        self.hly_bottom.addWidget(self.lbl_project_type)
        self.hly_bottom.addWidget(self.lbl_create_time)
        self.vly_1.addWidget(self.lbl_project_name)
        self.vly_1.addWidget(self.lbl_project_id)
        self.vly_1.addWidget(self.lbl_project_description)
        self.vly_1.addStretch(1)
        self.vly_1.addLayout(self.hly_bottom)
        self.setFixedSize(280, 240)

    def set_project_info(self, project_info: ProjectInfo):
        self.lbl_project_name.setText(project_info.project_name)
        self.lbl_project_id.setText(project_info.project_id)
        self.lbl_project_description.setText(project_info.project_description)
        self.lbl_project_type.setText(project_info.project_type.name)
        self.lbl_create_time.setText(project_info.create_time)
