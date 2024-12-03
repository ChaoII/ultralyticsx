import sys

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QApplication
from qfluentwidgets import SubtitleLabel, PrimaryToolButton

from common.component.custom_drawer import Drawer, DrawerPosition


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
        self.drawer = Drawer(position=DrawerPosition.Right, parent=self)
        # self.drawer.set_content_widget(self.cc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
