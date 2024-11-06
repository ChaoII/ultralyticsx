import sys
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame


class Drawer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: lightblue;")

        # 设置抽屉的高度与父窗口相同
        self.setFixedHeight(parent.height())
        self.move(0, 0)  # 初始位置在父窗口的右侧
        self.setGeometry(self.parent().geometry())

    def showDrawer(self):
        # 抽屉从右到左滑动
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(500)  # 动画时长为500毫秒
        animation.setStartValue(QRect(self.parent().width(), 0, 0, self.parent().height()))
        animation.setEndValue(QRect(self.parent().width() - 300, 0, 300, self.parent().height()))
        print(self.geometry())
        animation.start()
        print(self.geometry())

    def hideDrawer(self):
        # 抽屉从左到右滑动，隐藏
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(500)
        animation.setStartValue(QRect(self.parent().width() - 300, 0, 300, self.parent().height()))
        animation.setEndValue(QRect(self.parent().width(), 0, 0, self.parent().height()))
        animation.start()
        print(self.geometry())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("右到左抽屉动画")
        self.setGeometry(100, 100, 800, 600)  # 设置主窗口大小

        # 创建按钮来触发抽屉的显示和隐藏
        self.toggle_button = QPushButton("Toggle Drawer", self)
        self.toggle_button.clicked.connect(self.toggleDrawer)

        # 布局


        # 创建抽屉
        self.drawer = Drawer(self)

        self.isDrawerVisible = False

    def toggleDrawer(self):
        if self.isDrawerVisible:
            self.drawer.hideDrawer()
        else:
            self.drawer.showDrawer()
        self.isDrawerVisible = not self.isDrawerVisible

    def resizeEvent(self, event):
        # 确保当主窗口大小变化时，抽屉会自动调整高度和位置
        self.drawer.setFixedHeight(self.height())
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
