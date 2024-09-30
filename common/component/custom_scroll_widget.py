import overrides
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QLayout)
from qfluentwidgets import SingleDirectionScrollArea


class CustomScrollWidget(SingleDirectionScrollArea):

    def __init__(self, orient=Qt.Orientation.Vertical, parent=None):
        super().__init__(orient=orient, parent=parent)
        # 水平方向有很多组件
        self.scrollWidget = QWidget()
        # 必须要加这个方法
        self.setWidgetResizable(True)
        self.setWidget(self.scrollWidget)
        self._set_qss()

    @overrides.override()
    def setLayout(self, layout: QLayout) -> None:
        self.scrollWidget.setLayout(layout)

    def _set_qss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.setStyleSheet(
            """
            #scrollWidget {
                background-color: transparent;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }""")
