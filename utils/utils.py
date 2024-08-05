from loguru import logger
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

DARK_BG = "rgb(33,39,54)"
LIGHT_BG = "rgb(249, 249, 249)"


def log_info(message: str, color: str = "green") -> str:
    format_str = f"<span style = 'color:{color};white-space: pre' >{NOW} | {'INFO':<8} | {message}</span>"
    logger.info(message)
    return format_str


def log_warning(message: str, color: str = "yellow") -> str:
    format_str = f"<span style = 'color:{color};white-space: pre' >{NOW} | {'WARNING':<8} | {message}</span>"
    logger.warning(message)
    return format_str


def log_error(message: str, color: str = "red") -> str:
    format_str = f"<span style = 'color:{color};white-space: pre' >{NOW} | {'ERROR':<8} | {message}</span>"
    logger.error(message)
    return format_str


def format_log(message: str, color: str = "white", font_size: int = 20) -> str:
    format_str = f"<span style = 'color:{color};white-space: pre;font-size:{font_size}'>{message}</span>"
    return format_str


def show_center(widget: QWidget):
    desktop = QApplication.primaryScreen().availableGeometry()
    w, h = desktop.width(), desktop.height()
    widget.move(w // 2 - widget.width() // 2, h // 2 - widget.height() // 2)
    widget.show()
