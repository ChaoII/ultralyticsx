# coding:utf-8
import os
import sys

from PySide6.QtCore import Qt, QTranslator, QSize, Slot
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QSystemTrayIcon, QMenu
from qfluentwidgets import FluentIcon as FIcon, SystemTrayMenu, Action, MessageBox
from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            NavigationAvatarWidget, FluentTranslator, SubtitleLabel, setFont,
                            InfoBadge, InfoBadgePosition, SplashScreen)

from common.close_message_box import CustomMessageBox
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

        # splash_screen = SplashScreen(self.windowIcon(), self)
        # splash_screen.setIconSize(QSize(102, 102))
        # self.show_center()

        # create sub interface
        self.home_interface = HomeWidget(self)
        self.dataset_interface1 = DatasetWidget(self)
        self.dataset_interface = Widget('Interface1', self)
        self.train_interface = Widget('Interface2', self)
        self.val_interface = Widget('Val Interface', self)
        self.export_interface = Widget('Export Interface', self)
        self.test_interface = Widget('Test Interface', self)
        self.settingInterface = SettingInterface(self)
        self.init_navigation()

        # set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)
        self.init_system_tray()  # 初始化系统托盘
        self._connect_signals_and_slots()

        # splash_screen.finish()

    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())  # 设置托盘图标

        # 创建托盘菜单
        tray_menu = SystemTrayMenu(parent=self)
        action_show = Action(CustomFluentIcon.SHOW, "显示主窗口")
        tray_menu.addAction(action_show)
        action_show.triggered.connect(self.showNormal)

        action_exit = Action(CustomFluentIcon.EXIT, "退出")
        action_exit.triggered.connect(self._on_tray_exit_clicked)
        tray_menu.addAction(action_exit)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        # 托盘提示信息
        self.tray_icon.setToolTip("UltralyticsX")
        # 显示托盘图标
        self.tray_icon.show()

    def show_center(self):
        desktop = QApplication.primaryScreen().availableGeometry()
        cw = self.frameGeometry().width()  # 获取窗口当前宽度
        ch = self.frameGeometry().height()  # 获取窗口当前高度
        x = (desktop.width() - cw) // 2  # 使用整除以避免浮点数
        y = (desktop.height() - ch) // 2
        self.move(x, y)
        self.show()

    def init_navigation(self):
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
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.titleBar.closeBtn.clicked.disconnect(self.titleBar.window().close)
        self.titleBar.closeBtn.clicked.connect(self._on_close_clicked)

    @Slot(QSystemTrayIcon.ActivationReason)
    def on_tray_icon_activated(self, reason):
        """ 处理托盘图标的激活事件 """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def _hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "UltralyticsX 已隐藏",
            "点击托盘图标以显示。",
            QSystemTrayIcon.MessageIcon.Information,
            1000
        )

    def _on_tray_exit_clicked(self):
        self.home_interface.task_detail_widget.model_train_widget.stop_all_training_task()
        QApplication.quit()

    def _on_close_clicked(self):
        if cfg.get(cfg.remember_quit_status):
            if cfg.get(cfg.minimize_to_tray):
                self._hide_to_tray()
            else:
                QApplication.quit()
        else:
            msg_box = CustomMessageBox(self)
            msg_box.exec()
            if msg_box.get_accept_status():
                cfg.set(cfg.minimize_to_tray, False)
                self.close()
            else:
                cfg.set(cfg.minimize_to_tray, True)
                self._hide_to_tray()

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
