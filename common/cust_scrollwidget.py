import overrides
from PySide6.QtCore import Slot, Signal, Qt, QCoreApplication, QEasingCurve
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QGridLayout,
                               QSplitter, QLayout)
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon, \
    ProgressBar, TextEdit, InfoBar, InfoBarPosition, StateToolTip, FlowLayout, SingleDirectionScrollArea, isDarkTheme, \
    Theme, setTheme

from settings import cfg


class CustomScrollWidget(SingleDirectionScrollArea):

    def __init__(self, orient=Qt.Orientation.Vertical, parent=None):
        super().__init__(orient=orient, parent=parent)
        # 水平方向有很多组件
        self.scrollWidget = QWidget()
        # 必须要加这个方法
        self.setWidgetResizable(True)
        self.setWidget(self.scrollWidget)
        self._connect_signals_and_slot()
        self._set_qss()

    @overrides.override()
    def setLayout(self, layout: QLayout) -> None:
        self.scrollWidget.setLayout(layout)

    def _set_qss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _on_Theme_changed(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)
        # chang the theme of setting interface
        self._set_qss()

    def _connect_signals_and_slot(self):
        cfg.themeChanged.connect(self._on_Theme_changed)
