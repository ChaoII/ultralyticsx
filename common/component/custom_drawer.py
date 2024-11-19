import enum
import sys

from PySide6.QtGui import QColor, QShowEvent, QResizeEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFrame, \
    QGraphicsDropShadowEffect, QHBoxLayout
from PySide6.QtCore import QRect, QPropertyAnimation, QEasingCurve, Qt, QEvent, QSize
from qfluentwidgets import isDarkTheme, SimpleCardWidget, PrimaryToolButton, FluentIcon, themeColor, SubtitleLabel

from common.component.custom_icon import CustomFluentIcon
from common.component.fill_tool_button import FillToolButton


class DrawerPosition(enum.Enum):
    Left = 1
    Right = 2


class Drawer(QWidget):
    def __init__(self, parent: QWidget, position: DrawerPosition = DrawerPosition.Right):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setStyleSheet("background-color: lightblue;")

        self.btn_size = 30
        self.simple_card_widget = SimpleCardWidget(self)
        self.btn_collapse = FillToolButton(CustomFluentIcon.COLLAPSE_RIGHT)
        self.btn_collapse.set_border_radius(0)
        self.btn_collapse.setFixedSize(self.btn_size, self.btn_size)
        self.vly_button = QVBoxLayout()
        self.vly_button.setContentsMargins(0, 0, 0, 0)
        self.vly_button.setSpacing(0)
        self.vly_button.addWidget(self.btn_collapse)
        self.vly_button.addStretch(1)
        self.hly_content = QHBoxLayout(self)
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self.hly_content.setSpacing(0)
        if position == DrawerPosition.Right:
            self.hly_content.addLayout(self.vly_button)
            self.hly_content.addWidget(self.simple_card_widget)
            self.btn_collapse.set_icon(CustomFluentIcon.EXPAND_RIGHT.icon(color=themeColor()))
        else:
            self.hly_content.addWidget(self.simple_card_widget)
            self.hly_content.addLayout(self.vly_button)
            self.btn_collapse.set_icon(CustomFluentIcon.EXPAND_LEFT.icon(color=themeColor()))
        self.vly_content = QVBoxLayout(self.simple_card_widget)
        self.vly_content.setContentsMargins(0, 0, 0, 0)

        self.cur_width: int = 0
        self.collapse_geometry = self.geometry()
        self.full_geometry = self.geometry()
        self.position = position
        self.window().installEventFilter(self)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_collapse = True
        self.content_widget: None | QWidget = None
        self.init_drawer()
        self.btn_collapse.clicked.connect(self.on_btn_collapse_clicked)

        self.setShadowEffect(blurRadius=10)

    def on_btn_collapse_clicked(self):
        if self.is_collapse:
            self.show_drawer()
            if self.position == DrawerPosition.Right:
                self.btn_collapse.set_icon(CustomFluentIcon.COLLAPSE_RIGHT.icon(color=themeColor()))
            else:
                self.btn_collapse.set_icon(CustomFluentIcon.COLLAPSE_LEFT.icon(color=themeColor()))
        else:
            self.close_drawer()
            if self.position == DrawerPosition.Right:
                self.btn_collapse.set_icon(CustomFluentIcon.EXPAND_RIGHT.icon(color=themeColor()))
            else:
                self.btn_collapse.set_icon(CustomFluentIcon.EXPAND_LEFT.icon(color=themeColor()))

    def setShadowEffect(self, blurRadius=60, offset=(5, 5), color=QColor(255, 255, 0, 100)):
        """ add shadow to dialog """
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setBlurRadius(blurRadius)
        shadowEffect.setOffset(*offset)
        shadowEffect.setColor(color)
        self.setGraphicsEffect(shadowEffect)

    def set_content_widget(self, widget: QWidget):
        if self.content_widget:
            self.vly_content.removeWidget(self.content_widget)
        self.content_widget = widget
        self.vly_content.addWidget(self.content_widget)

    def init_drawer(self):
        self.cur_width = int(0.25 * self.parent().width()) + self.btn_size
        if self.position == DrawerPosition.Right:
            self.collapse_geometry = QRect(self.parent().width() - self.btn_size, 0,
                                           self.cur_width,
                                           self.parent().height())
            self.full_geometry = QRect(self.parent().width() - self.cur_width,
                                       0,
                                       self.cur_width,
                                       self.parent().height())
        elif self.position == DrawerPosition.Left:
            self.collapse_geometry = QRect(-self.cur_width + self.btn_size, 0, self.cur_width, self.parent().height())
            self.full_geometry = QRect(0, 0, self.cur_width, self.parent().height())
            # 默认为折叠状态
        if self.is_collapse:
            self.setGeometry(self.collapse_geometry)
        else:
            self.setGeometry(self.full_geometry)

    def eventFilter(self, obj, e: QEvent):
        if obj is self.window():
            if e.type() == QEvent.Type.Resize:
                self.init_drawer()
        return super().eventFilter(obj, e)

    def set_width(self, width):
        self.cur_width = width
        self.setFixedWidth(width)

    def show_drawer(self):
        if not self.is_collapse:
            return
        self.animation.setStartValue(self.collapse_geometry)
        self.animation.setEndValue(self.full_geometry)
        self.animation.start()
        self.is_collapse = False

    def close_drawer(self):
        if self.is_collapse:
            return
        self.animation.setStartValue(self.full_geometry)
        self.animation.setEndValue(self.collapse_geometry)
        self.animation.start()
        self.is_collapse = True


class CCC(QWidget):
    def __init__(self):
        super().__init__()
        self.vly = QVBoxLayout(self)
        self.btn = PrimaryToolButton()
        self.lbl = SubtitleLabel("Hello World as dasd ", self)
        self.lbl1 = SubtitleLabel("Hello World as dasd ", self)
        self.lbl2 = SubtitleLabel("Hello World as dasd ", self)
        self.lbl3 = SubtitleLabel("Hello World as dasd ", self)
        self.lbl4 = SubtitleLabel("Hello World as dasd ", self)
        self.vly.addWidget(self.btn)
        self.vly.addWidget(self.lbl)
        self.vly.addWidget(self.lbl1)
        self.vly.addWidget(self.lbl2)
        self.vly.addWidget(self.lbl3)
        self.vly.addWidget(self.lbl4)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cc = CCC()
        self.setWindowTitle("PyQt Drawer Example")
        self.resize(800, 600)
        self.drawer = Drawer(position=DrawerPosition.Left, parent=self)
        self.drawer.set_content_widget(self.cc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
