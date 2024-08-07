# coding:utf-8
import sys
import os

from utils.utils import show_center
from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            NavigationAvatarWidget, FluentTranslator, SubtitleLabel, setFont,
                            InfoBadge, InfoBadgePosition)
from qfluentwidgets import FluentIcon as FIcon

from settings import SettingInterface, cfg
from model_train import ModelTrainWidget
from dataset_process import DataProcessWidget


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

        # create sub interface
        self.home_interface = Widget('Search Interface', self)
        self.dataset_interface = DataProcessWidget(self)
        self.train_interface = ModelTrainWidget(self)
        self.val_interface = Widget('Val Interface', self)
        self.export_interface = Widget('Export Interface', self)
        self.test_interface = Widget('Test Interface', self)
        self.settingInterface = SettingInterface(self)
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.home_interface, FIcon.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()
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

        self.stackedWidget.currentChanged.connect(lambda: print(self.stackedWidget.currentWidget()))

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('./resource/images/ux.png'))
        self.setWindowTitle('UltralyticsX')

        # set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)


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
