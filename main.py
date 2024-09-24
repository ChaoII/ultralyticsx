# coding:utf-8
import os
import sys

from PySide6.QtCore import Qt, QTranslator, QSize, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import FluentIcon as FIcon
from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            NavigationAvatarWidget, FluentTranslator, SubtitleLabel, setFont,
                            InfoBadge, InfoBadgePosition, SplashScreen)

from common.custom_icon import CustomFluentIcon
from common.utils import show_center
from core.interface_base import InterfaceBase
from dataset import DatasetWidget
from home import HomeWidget
from settings import SettingInterface, cfg


class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(FluentWindow):
    def __init__(self):
        super().__init__()

        self.resize(1280, 800)
        self.setWindowIcon(QIcon('./resource/images/ux.png'))
        self.setWindowTitle('UltralyticsX')

        splash_screen = SplashScreen(self.windowIcon(), self)
        splash_screen.setIconSize(QSize(102, 102))
        self.show_center()

        # create sub interface
        self.home_interface = HomeWidget(self)
        self.dataset_interface1 = DatasetWidget(self)
        self.dataset_interface = Widget('Interface1', self)
        self.train_interface = Widget('Interface2', self)
        self.val_interface = Widget('Val Interface', self)
        self.export_interface = Widget('Export Interface', self)
        self.test_interface = Widget('Test Interface', self)
        self.settingInterface = SettingInterface(self)
        self.initNavigation()

        # set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)
        self._connect_signals_and_slots()

        splash_screen.finish()

    def show_center(self):
        desktop = QApplication.primaryScreen().availableGeometry()
        cw = self.frameGeometry().width()  # 获取窗口当前宽度
        ch = self.frameGeometry().height()  # 获取窗口当前高度
        x = (desktop.width() - cw) // 2  # 使用整除以避免浮点数
        y = (desktop.height() - ch) // 2
        self.move(x, y)
        self.show()

    def initNavigation(self):
        self.addSubInterface(self.home_interface, FIcon.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.dataset_interface1, CustomFluentIcon.DATASET1, self.tr('dataset1'))
        self.addSubInterface(self.dataset_interface, FIcon.PHOTO, self.tr('dataset'))
        self.addSubInterface(self.train_interface, FIcon.IOT, self.tr('model train'))
        self.addSubInterface(self.val_interface, FIcon.BOOK_SHELF, self.tr('model valid'))
        self.addSubInterface(self.export_interface, FIcon.UP, self.tr('model export'))
        self.addSubInterface(self.test_interface, FIcon.TILES, self.tr('model test'))

        self.navigationInterface.addSeparator()

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('zhiyiYo', 'resource/shoko.png'),
            onClick=lambda: print("------"),
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIcon.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # add badge to navigation item
        item = self.navigationInterface.widget(self.export_interface.objectName())
        InfoBadge.attension(
            text=9,
            parent=item.parent(),
            target=item,
            position=InfoBadgePosition.NAVIGATION_ITEM
        )

        # NOTE: enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

    def _connect_signals_and_slots(self):
        self.stackedWidget.currentChanged.connect(self._on_widget_changed)

    @Slot(int)
    def _on_widget_changed(self, index: int):
        item = self.stackedWidget.currentWidget()
        if isinstance(item, InterfaceBase):
            item.update_widget()


if __name__ == '__main__':
    if cfg.get(cfg.dpi_scale) == "auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    else:
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", "resource/i18n")
    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)
    # create main window
    w = Window()
    show_center(w)
    app.exec()
