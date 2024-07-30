from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt


class HeaderWidget(QFrame):
    def __init__(self):
        super(HeaderWidget, self).__init__()
        self.setFixedHeight(50)
        # 不设置样式不起作用
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(8, 8, 8, 8)
        self.lbl_logo = QLabel()
        self.lbl_logo.setFixedWidth(200)
        self.lbl_logo.setScaledContents(True)
        self.lbl_logo.setPixmap(QPixmap("images/logo.png"))
        self.settings = QToolButton()
        self.settings.setText("设置")
        self.settings.setIcon(QIcon("images/setting.png"))
        self.settings.ToolButtonPopupMode = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

        self.minimize = QToolButton()
        self.minimize.setText("最小化")
        self.minimize.setIcon(QIcon("images/minimize.png"))

        self.maximize = QToolButton()
        self.maximize.setText("最大化")
        self.maximize.setIcon(QIcon("images/maximize.png"))

        self.close = QToolButton()
        self.close.setText("关闭")
        self.close.setIcon(QIcon("images/close.png"))

        h_layout.addWidget(self.lbl_logo)
        h_layout.addStretch(1)
        h_layout.addWidget(self.settings)
        h_layout.addWidget(self.minimize)
        h_layout.addWidget(self.maximize)
        h_layout.addWidget(self.close)

        self.setLayout(h_layout)
