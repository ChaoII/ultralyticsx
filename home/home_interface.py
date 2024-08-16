import os
import time
from pathlib import Path

from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QFormLayout)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme, HorizontalPipsPager, ComboBox
from common.cust_scrollwidget import CustomScrollWidget
from common.page_widget import PipsPager, PipsScrollButtonDisplayMode
from settings import cfg
from .project_card import ProjectCard
from .new_project import NewProject, ProjectInfo


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

        self._connect_signals_and_slot()

    def _flush_flowlayout(self):
        # 移除全部组件
        self.layout.removeAllWidgets()
        # 重新添加组件
        for index in range(self.layout.count()):
            item = self.layout.itemAt(index)
            if item.widget():
                widget = item.widget()
                self.layout.addWidget(widget)

    def _connect_signals_and_slot(self):
        self.btn_create_project.clicked.connect(self._on_clicked_create_project)
        self.cmb_sort.currentIndexChanged.connect(self._on_load_projects())

    def _on_clicked_create_project(self):
        self.new_project_window = NewProject(self)
        self.new_project_window.project_created.connect(self._on_add_new_project)
        self.new_project_window.exec()

    @Slot(int)
    def _on_load_projects(self):
        # todo
        pass

    @Slot(ProjectInfo)
    def _on_add_new_project(self, project_info: ProjectInfo):
        self.project_card = ProjectCard()
        self.project_card.set_project_info(project_info)
        self.layout.addWidget(self.project_card)
        # 创建一个目录
        os.makedirs(Path(project_info.worker_dir) / project_info.project_id, exist_ok=True)
