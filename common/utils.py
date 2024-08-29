import os
import shutil
import sys
from pathlib import Path

from loguru import logger
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QColor
from random import randint
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

DARK_BG = "rgb(33,39,54)"
LIGHT_BG = "rgb(249, 249, 249)"


def format_datatime(data_time: datetime, fmt="%Y-%m-%d %H:%M:%S") -> str:
    return data_time.strftime(fmt)


def open_directory(directory: Path):
    if sys.platform.startswith('win'):
        os.startfile(directory)
    elif sys.platform.startswith('darwin'):  # macOS
        import subprocess
        subprocess.Popen(['open', directory])
    else:  # Linux
        import subprocess
        subprocess.Popen(['xdg-open', directory])


def str_to_datetime(datetime_str: str, fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(datetime_str, fmt)


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


def copy_tree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d, symlinks, ignore)


def generate_color_map(classes: int):
    colors = []
    for _ in range(classes):
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        colors.append(QColor(r, g, b))
    return colors


def generate_random_color() -> QColor:
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return QColor(r, g, b)


def invert_color(color):
    # 获取原始颜色的RGB值
    red = color.red()
    green = color.green()
    blue = color.blue()

    # 对RGB值取反
    inverted_red = 255 - red
    inverted_green = 255 - green
    inverted_blue = 255 - blue

    # 创建一个新的QColor对象，包含取反后的RGB值
    inverted_color = QColor(inverted_red, inverted_green, inverted_blue)

    # 返回取反后的颜色
    return inverted_color
