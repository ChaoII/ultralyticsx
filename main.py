# coding:utf-8
import os
import sys

from annotation.annotation_interface import AnnotationInterface
from common.core.window_manager import window_manager

from PySide6.QtCore import Qt, QTranslator, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QSystemTrayIcon
from qfluentwidgets import FluentIcon as FIcon, SystemTrayMenu, Action
from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            NavigationAvatarWidget, FluentTranslator, SubtitleLabel, setFont,
                            InfoBadge, InfoBadgePosition)

from common.component.close_message_box import CustomMessageBox
from common.component.custom_icon import CustomFluentIcon
from common.utils.utils import show_center
from common.core.interface_base import InterfaceBase
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
        self.setWindowTitle('Ultraly UI')
        self.setObjectName("main_widget")
        # splash_screen = SplashScreen(self.windowIcon(), self)
        # splash_screen.setIconSize(QSize(102, 102))
        # self.show_center()

        # create sub interface
        self.home_interface = HomeWidget(self)
        self.dataset_interface = DatasetWidget(self)
        self.annotation_interface = AnnotationInterface(self)
        self.train_interface = Widget('Interface2', self)
        self.val_interface = Widget('Val Interface', self)
        self.export_interface = Widget('Export Interface', self)
        self.test_interface = Widget('Test Interface', self)
        self.settingInterface = SettingInterface(self)
        self.init_navigation()

        # set the minimum window width that allows the navigation panel to be expanded
        self.navigationInterface.setExpandWidth(200)
        self.navigationInterface.expand(useAni=False)
        self.init_system_tray()  # 初始化系统托盘
        self._connect_signals_and_slots()

        # splash_screen.finish()
        window_manager.register_window("main_widget", self)

    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())  # 设置托盘图标

        # 创建托盘菜单
        tray_menu = SystemTrayMenu(parent=self)
        action_show = Action(CustomFluentIcon.SHOW, self.tr("Show main window"))
        tray_menu.addAction(action_show)
        action_show.triggered.connect(self.showNormal)

        action_exit = Action(CustomFluentIcon.EXIT, self.tr("Exit"))
        action_exit.triggered.connect(self._on_tray_exit_clicked)
        tray_menu.addAction(action_exit)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        # 托盘提示信息
        self.tray_icon.setToolTip("Ultraly UI")
        # 显示托盘图标
        self.tray_icon.show()

    def init_navigation(self):
        self.addSubInterface(self.home_interface, FIcon.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.dataset_interface, CustomFluentIcon.DATASET1, self.tr('Dataset'))
        self.addSubInterface(self.annotation_interface, CustomFluentIcon.ANNOTATION, self.tr('Data annotation'))
        self.addSubInterface(self.train_interface, FIcon.IOT, self.tr('Model train'))
        self.addSubInterface(self.val_interface, FIcon.BOOK_SHELF, self.tr('Model valid'))
        self.addSubInterface(self.export_interface, FIcon.UP, self.tr('Model export'))
        self.addSubInterface(self.test_interface, FIcon.TILES, self.tr('Model test'))

        self.navigationInterface.addSeparator()

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('zhiyiYo', 'resource/shoko.png'),
            onClick=lambda: print("------"),
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIcon.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

        # add badge to navigation item
        item = self.navigationInterface.widget(self.export_interface.objectName())
        InfoBadge.attension(
            text=9,
            parent=item.parent(),
            target=item,
            position=InfoBadgePosition.NAVIGATION_ITEM
        )

    def _connect_signals_and_slots(self):
        self.stackedWidget.currentChanged.connect(self._on_widget_changed)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.titleBar.closeBtn.clicked.disconnect(self.titleBar.window().close)
        self.titleBar.closeBtn.clicked.connect(self._on_close_clicked)
        # 设置云母特效
        cfg.enable_mica_effect.valueChanged.connect(self.setMicaEffectEnabled)

    @Slot(QSystemTrayIcon.ActivationReason)
    def on_tray_icon_activated(self, reason):
        """ 处理托盘图标的激活事件 """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def _hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            self.tr("Ultraly UI hided into tray"),
            self.tr("Click tray to show main window"),
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
    def _on_widget_changed(self, _):
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
    settingTranslator.load(locale, "ultralytics_ui", ".", "resource/i18n")
    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)
    # create main window
    w = Window()
    # 设置云母特效
    w.setMicaEffectEnabled(cfg.get(cfg.enable_mica_effect))
    show_center(w)
    app.exec()
