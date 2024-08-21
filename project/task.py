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

        # self.horizontalHeader().setStretchLastSection(True)
        # songInfos = [
        #     ['かばん', 'aiko', 'かばん', '2004', '5:04'],
        #     ['爱你', '王心凌', '爱你', '2004', '3:39'],
        #     ['星のない世界', 'aiko', '星のない世界/横顔', '2007', '5:30'],
        #     ['横顔', 'aiko', '星のない世界/横顔', '2007', '5:06'],
        #     ['秘密', 'aiko', '秘密', '2008', '6:27'],
        #     ['シアワセ', 'aiko', '秘密', '2008', '5:25'],
        #     ['二人', 'aiko', '二人', '2008', '5:00'],
        #     ['スパークル', 'RADWIMPS', '君の名は。', '2016', '8:54'],
        #     ['なんでもないや', 'RADWIMPS', '君の名は。', '2016', '3:16'],
        #     ['前前前世', 'RADWIMPS', '人間開花', '2016', '4:35'],
        #     ['恋をしたのは', 'aiko', '恋をしたのは', '2016', '6:02'],
        #     ['夏バテ', 'aiko', '恋をしたのは', '2016', '4:41'],
        #     ['もっと', 'aiko', 'もっと', '2016', '4:50'],
        #     ['問題集', 'aiko', 'もっと', '2016', '4:18'],
        #     ['半袖', 'aiko', 'もっと', '2016', '5:50'],
        #     ['ひねくれ', '鎖那', 'Hush a by little girl', '2017', '3:54'],
        #     ['シュテルン', '鎖那', 'Hush a by little girl', '2017', '3:16'],
        #     ['愛は勝手', 'aiko', '湿った夏の始まり', '2018', '5:31'],
        #     ['ドライブモード', 'aiko', '湿った夏の始まり', '2018', '3:37'],
        #     ['うん。', 'aiko', '湿った夏の始まり', '2018', '5:48'],
        #     ['キラキラ', 'aikoの詩。', '2019', '5:08', 'aiko'],
        #     ['恋のスーパーボール', 'aiko', 'aikoの詩。', '2019', '4:31'],
        #     ['磁石', 'aiko', 'どうしたって伝えられないから', '2021', '4:24'],
        #     ['食べた愛', 'aiko', '食べた愛/あたしたち', '2021', '5:17'],
        #     ['列車', 'aiko', '食べた愛/あたしたち', '2021', '4:18'],
        #     ['花の塔', 'さユり', '花の塔', '2022', '4:35'],
        #     ['夏恋のライフ', 'aiko', '夏恋のライフ', '2022', '5:03'],
        #     ['あかときリロード', 'aiko', 'あかときリロード', '2023', '4:04'],
        #     ['荒れた唇は恋を失くす', 'aiko', '今の二人をお互いが見てる', '2023', '4:07'],
        #     ['ワンツースリー', 'aiko', '今の二人をお互いが見てる', '2023', '4:47'],
        # ]
        # for i, songInfo in enumerate(songInfos):
        #     for j in range(5):
        #         if j == 4:
        #             self.setCellWidget(i, j, OperationWidget())
        #         else:
        #             self.setItem(i, j, QTableWidgetItem(songInfo[j]))


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
