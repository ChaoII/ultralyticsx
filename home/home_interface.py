import os
import shutil
from pathlib import Path

from PySide6.QtCore import Slot, Signal, Qt, QEasingCurve
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QFormLayout)
from qfluentwidgets import BodyLabel, PrimaryPushButton, FluentIcon, \
    FlowLayout, ComboBox
from sqlalchemy import desc, asc
from sqlalchemy.orm import Query

from common.cust_scrollwidget import CustomScrollWidget
from common.db_helper import db_session
from common.page_widget import PipsPager, PipsScrollButtonDisplayMode
from common.utils import str_to_datetime, format_datatime
from models.models import Project
from .new_project import NewProject, ProjectInfo
from .project_card import ProjectCard


class HomeWidget(QWidget):
    start_train_model_signal = Signal(str, int, int, float, int)
    stop_train_model_signal = Signal()

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        self.setObjectName("home_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hvy_btn = QHBoxLayout()
        self.btn_create_project = PrimaryPushButton(FluentIcon.ADD, self.tr("Create project"))
        self.lbl_sort = BodyLabel(self.tr("sort:"), self)
        self.cmb_sort = ComboBox()
        self.cmb_sort.setMinimumWidth(200)
        self.cmb_sort.addItems([self.tr("time ascending"),
                                self.tr("time descending"),
                                self.tr("name ascending"),
                                self.tr("name descending")])
        self.fly_sort = QFormLayout()
        self.fly_sort.addRow(self.lbl_sort, self.cmb_sort)
        self.hvy_btn.addWidget(self.btn_create_project)
        self.hvy_btn.addStretch(1)
        self.hvy_btn.addLayout(self.fly_sort)

        self.scroll_area = CustomScrollWidget(orient=Qt.Orientation.Vertical)
        self.layout = FlowLayout(needAni=False)  # 启用动画
        self.layout.setAnimation(250, QEasingCurve.Type.OutQuad)
        self.scroll_area.setLayout(self.layout)

        self.vly.addLayout(self.hvy_btn)
        self.vly.addWidget(self.scroll_area)
        pager = PipsPager()
        pager.setPageNumber(15)
        pager.setVisibleNumber(8)

        # 始终显示前进和后退按钮
        pager.setNextButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        pager.setPreviousButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        self.vly.addWidget(pager)

        self._load_projects()
        self._connect_signals_and_slot()

    def _connect_signals_and_slot(self):
        self.btn_create_project.clicked.connect(self._on_clicked_create_project)
        self.cmb_sort.currentIndexChanged.connect(self._on_sorting_changed)

    def _on_clicked_create_project(self):
        self.new_project_window = NewProject(self)
        self.new_project_window.project_created.connect(self._on_add_new_project)
        self.new_project_window.exec()

    def _clear_project_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if isinstance(item, ProjectCard):
                item.deleteLater()

    @Slot(int)
    def _on_sorting_changed(self, index):
        self._load_projects()

    def _load_projects(self):
        field = Project.project_name
        order = asc
        if self.cmb_sort.currentIndex() == 0:
            field = Project.create_time
            order = asc
        if self.cmb_sort.currentIndex() == 1:
            field = Project.create_time
            order = desc
        if self.cmb_sort.currentIndex() == 2:
            field = Project.project_name
            order = asc
        if self.cmb_sort.currentIndex() == 3:
            field = Project.project_name
            order = desc

        self._clear_project_layout()
        with db_session() as session:
            query: Query = session.query(Project)
            result: list[Project] = query.order_by(order(field)).all()
            # 转成json
            # json_result = json.dumps([user.__dict__ for user in result], default=str)
            for row in result:
                project_info = ProjectInfo()
                project_info.project_name = row.project_name
                project_info.project_id = row.project_id
                project_info.project_description = row.project_description
                project_info.create_time = format_datatime(row.create_time)
                project_info.worker_dir = row.worker_dir
                self._add_new_project(project_info)

    def _add_new_project(self, project_info: ProjectInfo):
        self.project_card = ProjectCard()
        self.project_card.delete_clicked.connect(self._on_delete_project_card)
        self.project_card.view_clicked.connect(self._on_view_project_detail)
        self.project_card.set_project_info(project_info)
        self.layout.addWidget(self.project_card)

    @Slot(str)
    def _on_delete_project_card(self, project_id):
        with db_session(auto_commit_exit=True) as session:
            record = session.query(Project).filter_by(project_id=project_id).first()
            session.delete(record)
        shutil.rmtree(Path(record.worker_dir) / project_id)
        self._load_projects()

    @Slot()
    def _on_view_project_detail(self):
        pass

    @Slot(ProjectInfo)
    def _on_add_new_project(self, project_info: ProjectInfo):
        self._add_new_project(project_info)
        # 创建一个目录
        new_project_row = Project(
            project_name=project_info.project_name,
            project_id=project_info.project_id,
            project_description=project_info.project_description,
            project_type=project_info.project_type.value,
            worker_dir=project_info.worker_dir,
            create_time=str_to_datetime(project_info.create_time),
        )
        # 这里想获取新增后的id,需要refresh数据，就不能在上下文里提交
        with db_session(True) as session:
            session.add(new_project_row)
        os.makedirs(Path(project_info.worker_dir) / project_info.project_id, exist_ok=True)
