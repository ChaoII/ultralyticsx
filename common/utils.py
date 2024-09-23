import enum
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from random import randint

from PIL import Image
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget
from loguru import logger

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class CustomColor(enum.Enum):
    RED = [QColor("#FF0000"), QColor("#FF6347")]  # 红色
    BLUE = [QColor("#003366"), QColor("#007BFF")]  # 蓝色（深蓝色）（亮蓝色）
    PURPLE = [QColor("#6A0DAD"), QColor("#BF77F6")]  # 紫色（深紫色）（亮紫色）
    CYAN = [QColor("#006400"), QColor("#00FFBF")]  # 青色（深绿色，接近青色）（亮青色）
    CYAN1 = [QColor("#004080"), QColor("#87CEEB")]  # 青色1（海军蓝，接近青色）（天青色）
    ORANGE = [QColor("#FF4500"), QColor("#FFA500")]  # 橙色（橙色红）（纯橙色）
    YELLOW = [QColor("#968911"), QColor("#FFFF00")]  # 黄色（金色，接近黄色）（纯黄色）
    PINK = [QColor("#FF69B4"), QColor("#FFC0CB")]  # 粉色（深粉色）（粉红色）
    GRAY = [QColor("#606060"), QColor("#C0C0C0")]  # 灰色（深灰色）（浅灰色）
    BROWN = [QColor("#A52A2A"), QColor("#D2691E")]  # 棕色（深棕色）（浅棕色）
    GREEN = [QColor("#1E9000"), QColor("#2ECC71")]  # 绿色（深绿色）（亮绿色）

    def light_color(self):
        return self.value[0]

    def dark_color(self):
        return self.value[1]


def format_datatime(data_time: datetime, fmt="%Y-%m-%d %H:%M:%S") -> str:
    if not data_time:
        return ""
    return data_time.strftime(fmt)


def str_to_datetime(datetime_str: str, fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(datetime_str, fmt)


def open_directory(directory: Path):
    if sys.platform.startswith('win'):
        os.startfile(directory)
    elif sys.platform.startswith('darwin'):  # macOS
        import subprocess
        subprocess.Popen(['open', directory])
    else:  # Linux
        import subprocess
        subprocess.Popen(['xdg-open', directory])


def log_info(message: str, color: str = "green", apply_rich_text=False) -> str:
    if apply_rich_text:
        format_str = f"<span style = 'color:{color};white-space: pre' >{NOW} | {'INFO':<8} | {message}</span>"
    else:
        format_str = f"{NOW} | {'INFO':<8} | {message}"
    logger.info(message)
    return format_str


def log_warning(message: str, color: str = "yellow", apply_rich_text=False) -> str:
    if apply_rich_text:
        format_str = f"<span style = 'color:{color};white-space: pre' >{NOW} | {'WARNING':<8} | {message}</span>"
    else:
        format_str = f"{NOW} | {'WARNING':<8} | {message}"
    logger.warning(message)
    return format_str


def log_error(message: str, color: str = "red", apply_rich_text=False) -> str:
    if apply_rich_text:
        format_str = f"<span style = 'color:{color};white-space: pre' >{NOW} | {'ERROR':<8} | {message}</span>"
    else:
        format_str = f"{NOW} | {'ERROR':<8} | {message}"
    logger.error(message)
    return format_str


def format_log(message: str, color: str = "white", font_size: int = 20) -> str:
    format_str = f"<span style = 'color:{color};white-space: pre;font-size:{font_size}'>{message}</span>"
    return format_str


def show_center(widget: QWidget):
    desktop = QApplication.primaryScreen().availableGeometry()
    cw = widget.frameGeometry().width()  # 获取窗口当前宽度
    ch = widget.frameGeometry().height()  # 获取窗口当前高度
    x = (desktop.width() - cw) // 2  # 使用整除以避免浮点数
    y = (desktop.height() - ch) // 2

    widget.move(x, y)
    widget.show()


def copy_tree(src, dst: Path, symlinks=False, ignore=None):
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d, symlinks, ignore)
        elif os.path.isfile(s):
            shutil.copy(s, d)


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


def is_empty(folder_path: Path):
    return not any(folder_path.iterdir())


def is_image(filename):
    try:
        with Image.open(filename) as img:
            img.verify()  # 验证图片是否完整
            return True
    except (IOError, SyntaxError) as e:
        return False
