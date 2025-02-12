from PySide6.QtCore import QObject, Qt
from qfluentwidgets import InfoBar, InfoBarPosition

from common.core.window_manager import window_manager


def raise_error(error_message: str):
    InfoBar.error(
        title='',
        content=error_message,
        orient=Qt.Orientation.Vertical,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=-1,
        parent=window_manager.find_window("main_widget")
    )
