from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme
from common.cust_scrollwidget import CustomScrollWidget
from settings import cfg
from .project_card import ProjectCard
from .new_project import NewProject


class HomeWidget(QWidget):
    start_train_model_signal = Signal(str, int, int, float, int)
    stop_train_model_signal = Signal()

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        self.setObjectName("home_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hvy_btn = QHBoxLayout()
        self.btn_stop_train = PrimaryPushButton(FluentIcon.ADD, self.tr("Add project"))
        self.hvy_btn.addWidget(self.btn_stop_train)
        self.hvy_btn.addStretch(1)

        self.scroll_area = CustomScrollWidget(orient=Qt.Orientation.Vertical)
        self.layout = FlowLayout(needAni=False)  # 启用动画
        self.layout.setAnimation(250, QEasingCurve.Type.OutQuad)
        self.scroll_area.setLayout(self.layout)
        for i in range(8):
            self.project_card = ProjectCard()
            self.layout.addWidget(self.project_card)

        self.vly.addLayout(self.hvy_btn)
        self.vly.addWidget(self.scroll_area)

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
        self.btn_stop_train.clicked.connect(self._on_clicked_create_project)

    def _on_clicked_create_project(self):
        self.new_project_window = NewProject(self)
        self.new_project_window.exec()
