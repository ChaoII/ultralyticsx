import sys
from PySide6.QtWidgets import (QApplication,
                               QPushButton, QVBoxLayout, QWidget,
                               QLabel, QLineEdit, QFileDialog, QTabWidget)
from PySide6.QtCore import Qt
from main import MainWindow
from header.header_widget import HeaderWidget


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(800, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 0, 0, 0)
        header_widget = HeaderWidget()
        main_windows = MainWindow()

        v_layout.addWidget(header_widget)
        v_layout.addWidget(main_windows)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("style.css", "r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec())
