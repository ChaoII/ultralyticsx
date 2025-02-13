from PySide6.QtCore import QObject, Qt
from qfluentwidgets import InfoBar, InfoBarPosition

from common.core.window_manager import window_manager


def raise_error(title: str, error_message: str, duration: int = -1):
    InfoBar.error(
        title=title,
        content=error_message,
        orient=Qt.Orientation.Vertical,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=duration,
        parent=window_manager.find_window("main_widget")
    )


def raise_warning(title: str, error_message: str, duration: int = 5000):
    InfoBar.warning(
        title=title,
        content=error_message,
        orient=Qt.Orientation.Vertical,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=duration,
        parent=window_manager.find_window("main_widget")
    )
