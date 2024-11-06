import enum
import sys

from PySide6.QtGui import QColor, QShowEvent, QResizeEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFrame, \
    QGraphicsDropShadowEffect
from PySide6.QtCore import QRect, QPropertyAnimation, QEasingCurve, Qt, QEvent, QSize
from qfluentwidgets import isDarkTheme


class DrawerPosition(enum.Enum):
    Left = 1
    Right = 2


class Drawer(QWidget):
    def __init__(self, parent: QWidget, position: DrawerPosition):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: lightblue;")
        self.widget = QFrame()
        self.vly_content = QVBoxLayout(self)

        self.cur_width: int = 0
        self.cur_geometry = self.geometry()
        self.position = position
        self.window().installEventFilter(self)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_collapse = True
        self.content_widget: None | QWidget = None
        self.init_drawer()
        self.set_content_widget(self.widget)

        self.setShadowEffect(blurRadius=60)

    def setShadowEffect(self, blurRadius=60, offset=(30, 10), color=QColor(255, 255, 0, 100)):
        """ add shadow to dialog """
        shadowEffect = QGraphicsDropShadowEffect(self.widget)
        shadowEffect.setBlurRadius(blurRadius)
        shadowEffect.setOffset(*offset)
        shadowEffect.setColor(color)
        self.widget.setGraphicsEffect(None)
        self.widget.setGraphicsEffect(shadowEffect)

    def set_content_widget(self, widget: QWidget):
        if self.content_widget:
            self.vly_content.removeWidget(self.content_widget)
        self.content_widget = widget
        self.vly_content.addWidget(self.content_widget)

    def init_drawer(self):
        self.cur_width = int(0.25 * self.parent().width())
        if self.position == DrawerPosition.Right:
            self.cur_geometry = QRect(self.parent().width() - self.cur_width,
                                      0, self.cur_width, self.parent().height())
            self.setGeometry(self.cur_geometry)
        elif self.position == DrawerPosition.Left:
            self.cur_geometry = QRect(0, 0, self.cur_width, self.parent().height())
            self.setGeometry(self.cur_geometry)

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
        self.show()
        if self.position == DrawerPosition.Right:
            start_geom = QRect(self.parent().width(), 0, 0, self.cur_geometry.height())
        else:
            start_geom = QRect(0, 0, 0, self.cur_geometry.height())
        self.animation.setStartValue(start_geom)
        self.animation.setEndValue(self.cur_geometry)
        self.animation.start()
        self.is_collapse = False

    def close_drawer(self):
        if self.is_collapse:
            return
        if self.position == DrawerPosition.Right:
            end_geom = QRect(self.parent().width(), 0, 0, self.cur_geometry.height())
        else:
            end_geom = QRect(0, 0, 0, self.cur_geometry.height())
        self.animation.setStartValue(self.cur_geometry)
        self.animation.setEndValue(end_geom)
        self.animation.start()
        self.is_collapse = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Drawer Example")
        self.resize(800, 600)

        self.drawer = Drawer(position=DrawerPosition.Right, parent=self)
        self.drawer.hide()

        button1 = QPushButton("Open Drawer", self)
        button1.setGeometry(10, 10, 100, 30)
        button1.clicked.connect(self.open_drawer)

        button1 = QPushButton("close Drawer", self)
        button1.setGeometry(10, 100, 100, 30)
        button1.clicked.connect(self.close_drawer)

    def open_drawer(self):
        self.drawer.show_drawer()

    def close_drawer(self):
        self.drawer.close_drawer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
