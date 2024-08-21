from pathlib import Path

from PySide6.QtCore import QRect, QPoint, Signal, QModelIndex, QSize
from PySide6.QtGui import QMouseEvent, QCursor, Qt, QPainter, QPen, QFont, QColor, QPainterPath, QPalette
from qfluentwidgets import ElevatedCardWidget, TransparentToolButton, StrongBodyLabel, TitleLabel, BodyLabel, \
    themeColor, \
    isDarkTheme, FluentIcon, CaptionLabel, TextWrap, TableWidget, TableItemDelegate, HyperlinkLabel, CommandBar, Action, \
    setCustomStyleSheet, FluentLabelBase, PrimaryPushButton
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QStyle, QStyleOption, QLineEdit, QHeaderView, \
    QStyleOptionViewItem, QTableWidgetItem, QPushButton, QWidget, QApplication

from common.utils import format_datatime
from models.models import Task
from project.new_project import ProjectInfo

from common.fill_tool_button import FillToolButton


class CustomLabel(HyperlinkLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setText(text)
        self.setUnderlineVisible(True)

    def setTextColor(self, light=QColor(0, 0, 0), dark=QColor(255, 255, 255)):
        setCustomStyleSheet(
            self,
            f"CustomLabel{{color:{light.name(QColor.NameFormat.HexArgb)}}}",
            f"CustomLabel{{color:{dark.name(QColor.NameFormat.HexArgb)}}}"
        )


class OperationWidget(QWidget):
    def __init__(self, task_id: str):
        super().__init__()
        self.hly_content = QHBoxLayout(self)
        self.btn_view = CustomLabel(self.tr("view"), self)
        self.btn_view.setTextColor(QColor(0, 0, 255))
        self.btn_delete = CustomLabel(self.tr("delete"), self)
        self.btn_delete.setTextColor(QColor(255, 0, 0))
        self.btn_open = CustomLabel(self.tr("open"), self)
        self.btn_open.setTextColor(QColor(0, 0, 255))

        self.hly_content.addStretch(1)
        self.hly_content.addWidget(self.btn_view)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_delete)
        self.hly_content.addWidget(CaptionLabel("|", self))
        self.hly_content.addWidget(self.btn_open)
        self.hly_content.addStretch(1)

        self.task_id = task_id


class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return

        if isDarkTheme():
            option.palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            option.palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        else:
            option.palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.red)
            option.palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.red)


class TaskTableWidget(TableWidget):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(6)
        self.setRowCount(24)
        self.setItemDelegate(CustomTableItemDelegate(self))
        self.setHorizontalHeaderLabels([
            self.tr('Task ID'), self.tr('Project name'), self.tr('Task status'),
            self.tr('Comment'), self.tr('Create time'), self.tr("Operation")
        ])
        self.setColumnWidth(0, 100)
        self.setColumnWidth(4, 160)
        self.setColumnWidth(5, 160)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)


class TaskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("task_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.hly_btn = QHBoxLayout()
        self.btn_create_task = PrimaryPushButton(FluentIcon.ADD, self.tr("Create task"))
        self.hly_btn.addWidget(self.btn_create_task)
        self.hly_btn.addStretch(1)
        self.tb_task = TaskTableWidget()
        self.vly.addLayout(self.hly_btn)
        self.vly.addWidget(self.tb_task)
        self._connect_signals_and_slots()

    def set_data(self, data: list[Task]):
        print("===", data)
        # self.tb_task.setItem()
        for i, task in enumerate(data):
            item0 = QTableWidgetItem(task.task_id)
            item1 = QTableWidgetItem(task.project.project_name)
            item2 = QTableWidgetItem(str(task.task_status))
            item3 = QTableWidgetItem(task.comment)
            item4 = QTableWidgetItem(format_datatime(task.create_time))
            item5 = OperationWidget(task.task_id)

            item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.tb_task.setItem(i, 0, item0)
            self.tb_task.setItem(i, 1, item1)
            self.tb_task.setItem(i, 2, item2)
            self.tb_task.setItem(i, 3, item3)
            self.tb_task.setItem(i, 4, item4)
            self.tb_task.setCellWidget(i, 5, item5)

    def _connect_signals_and_slots(self):
        self.btn_create_task.clicked.connect(self._on_create_task_clicked)

    def _on_create_task_clicked(self):
        pass
