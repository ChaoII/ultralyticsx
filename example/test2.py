import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import QPropertyAnimation, Property, Qt
from PySide6.QtGui import QPainter, QColor

class CollapsibleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # 创建主布局
        main_layout = QHBoxLayout(self)

        # 创建左侧固定宽度的 QWidget
        self.left_widget = QWidget(self)
        self.left_widget.setFixedWidth(200)
        self.left_widget.setStyleSheet("background-color: lightblue;")

        # 创建右侧可变宽度的 QWidget
        self.right_widget = QWidget(self)
        self.right_widget.setStyleSheet("background-color: lightgreen;")

        # 添加到主布局
        main_layout.addWidget(self.left_widget)
        main_layout.addWidget(self.right_widget)

        # 创建按钮
        self.btn_collapse = QPushButton("Toggle", self.right_widget)
        self.btn_collapse.setFixedSize(30, 30)
        self.btn_collapse.setStyleSheet("border-radius: 0px; background-color: white;")
        # self.btn_collapse.setZValue(100)
        self.btn_collapse.clicked.connect(self.toggle_animation)

        # 设置按钮初始位置
        self.update_button_position()

        # 初始化动画
        self.animation = QPropertyAnimation(self.right_widget, b"minimumWidth")
        self.animation.setDuration(500)  # 动画持续时间

    @Property(int)
    def minimumWidth(self):
        return self.right_widget.minimumWidth()

    @minimumWidth.setter
    def minimumWidth(self, value):
        self.right_widget.setMinimumWidth(value)

    def toggle_animation(self):
        if self.right_widget.minimumWidth() == 0:
            self.animation.setStartValue(0)
            self.animation.setEndValue(200)
        else:
            self.animation.setStartValue(200)
            self.animation.setEndValue(0)
        self.animation.start()

    def update_button_position(self):
        # 更新按钮位置，使其始终位于右上角
        self.btn_collapse.move(self.right_widget.width() - self.btn_collapse.width(), 0)

    def resizeEvent(self, event):
        # 重写 resizeEvent 方法，确保按钮位置正确
        super().resizeEvent(event)
        self.update_button_position()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CollapsibleWidget()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
