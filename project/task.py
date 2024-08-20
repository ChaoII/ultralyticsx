from pathlib import Path

from PySide6.QtCore import QRect, QPoint, Signal, QModelIndex, QSize
from PySide6.QtGui import QMouseEvent, QCursor, Qt, QPainter, QPen, QFont, QColor, QPainterPath, QPalette
from qfluentwidgets import ElevatedCardWidget, TransparentToolButton, StrongBodyLabel, TitleLabel, BodyLabel, \
    themeColor, \
    isDarkTheme, FluentIcon, CaptionLabel, TextWrap, TableWidget, TableItemDelegate, HyperlinkLabel, CommandBar, Action, \
    setCustomStyleSheet, FluentLabelBase, PrimaryPushButton
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QStyle, QStyleOption, QLineEdit, QHeaderView, \
    QStyleOptionViewItem, QTableWidgetItem, QPushButton, QWidget, QApplication
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
    def __init__(self):
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
        self.setColumnCount(5)
        self.setRowCount(24)
        self.setItemDelegate(CustomTableItemDelegate(self))
        self.setHorizontalHeaderLabels([
            self.tr('Task ID'), self.tr('Project'), self.tr('Task status'),
            self.tr('Create time'), self.tr('Comment'), self.tr("Operation")
        ])
        self.setColumnWidth(3, 200)
        self.setColumnWidth(4, 200)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        # self.horizontalHeader().setStretchLastSection(True)
        songInfos = [
            ['かばん', 'aiko', 'かばん', '2004', '5:04'],
            ['爱你', '王心凌', '爱你', '2004', '3:39'],
            ['星のない世界', 'aiko', '星のない世界/横顔', '2007', '5:30'],
            ['横顔', 'aiko', '星のない世界/横顔', '2007', '5:06'],
            ['秘密', 'aiko', '秘密', '2008', '6:27'],
            ['シアワセ', 'aiko', '秘密', '2008', '5:25'],
            ['二人', 'aiko', '二人', '2008', '5:00'],
            ['スパークル', 'RADWIMPS', '君の名は。', '2016', '8:54'],
            ['なんでもないや', 'RADWIMPS', '君の名は。', '2016', '3:16'],
            ['前前前世', 'RADWIMPS', '人間開花', '2016', '4:35'],
            ['恋をしたのは', 'aiko', '恋をしたのは', '2016', '6:02'],
            ['夏バテ', 'aiko', '恋をしたのは', '2016', '4:41'],
            ['もっと', 'aiko', 'もっと', '2016', '4:50'],
            ['問題集', 'aiko', 'もっと', '2016', '4:18'],
            ['半袖', 'aiko', 'もっと', '2016', '5:50'],
            ['ひねくれ', '鎖那', 'Hush a by little girl', '2017', '3:54'],
            ['シュテルン', '鎖那', 'Hush a by little girl', '2017', '3:16'],
            ['愛は勝手', 'aiko', '湿った夏の始まり', '2018', '5:31'],
            ['ドライブモード', 'aiko', '湿った夏の始まり', '2018', '3:37'],
            ['うん。', 'aiko', '湿った夏の始まり', '2018', '5:48'],
            ['キラキラ', 'aikoの詩。', '2019', '5:08', 'aiko'],
            ['恋のスーパーボール', 'aiko', 'aikoの詩。', '2019', '4:31'],
            ['磁石', 'aiko', 'どうしたって伝えられないから', '2021', '4:24'],
            ['食べた愛', 'aiko', '食べた愛/あたしたち', '2021', '5:17'],
            ['列車', 'aiko', '食べた愛/あたしたち', '2021', '4:18'],
            ['花の塔', 'さユり', '花の塔', '2022', '4:35'],
            ['夏恋のライフ', 'aiko', '夏恋のライフ', '2022', '5:03'],
            ['あかときリロード', 'aiko', 'あかときリロード', '2023', '4:04'],
            ['荒れた唇は恋を失くす', 'aiko', '今の二人をお互いが見てる', '2023', '4:07'],
            ['ワンツースリー', 'aiko', '今の二人をお互いが見てる', '2023', '4:47'],
        ]
        for i, songInfo in enumerate(songInfos):
            for j in range(5):
                # self.setItem(i, j, QTableWidgetItem(songInfo[j]))
                if j == 4:
                    self.setCellWidget(i, j, OperationWidget())
                else:
                    self.setItem(i, j, QTableWidgetItem(songInfo[j]))


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
