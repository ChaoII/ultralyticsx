import enum
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from random import randint
import numpy as np
from PIL import Image
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget
from loguru import logger
from snowflake import SnowflakeGenerator

snowflake_generator = SnowflakeGenerator(instance=0)


def NOW():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class Colors:
    def __init__(self):
        hexs = (
            "042AFF",
            "0BDBEB",
            "F3F3F3",
            "00DFB7",
            "111F68",
            "FF6FDD",
            "FF444F",
            "CCED00",
            "00F344",
            "BD00FF",
            "00B4FF",
            "DD00BA",
            "00FFFF",
            "26C000",
            "01FFB3",
            "7D24FF",
            "7B0068",
            "FF1B6C",
            "FC6D2F",
            "A2FF0B",
        )
        self.palette = [self.hex2rgb(f"#{c}") for c in hexs]
        self.n = len(self.palette)
        self.pose_palette = np.array(
            [
                [255, 128, 0],
                [255, 153, 51],
                [255, 178, 102],
                [230, 230, 0],
                [255, 153, 255],
                [153, 204, 255],
                [255, 102, 255],
                [255, 51, 255],
                [102, 178, 255],
                [51, 153, 255],
                [255, 153, 153],
                [255, 102, 102],
                [255, 51, 51],
                [153, 255, 153],
                [102, 255, 102],
                [51, 255, 51],
                [0, 255, 0],
                [0, 0, 255],
                [255, 0, 0],
                [255, 255, 255],
            ],
            dtype=np.uint8,
        )

    def __call__(self, i, bgr=False):
        """Converts hex color codes to RGB values."""
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):
        """Converts hex color codes to RGB values (i.e. default PIL order)."""
        return tuple(int(h[1 + i: 1 + i + 2], 16) for i in (0, 2, 4))


colors = Colors()


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


def format_time_delta(delta: timedelta) -> str:
    days = delta.days
    seconds = delta.seconds
    # 将秒数转换为小时、分钟和秒
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_hours = days * 24 + seconds / 3600
    return f"{total_hours:.2f}h"


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
        format_str = f"<span style = 'color:{color};white-space: pre' >{NOW()} | {'INFO':<8} | {message}</span>"
    else:
        format_str = f"{NOW()} | {'INFO':<8} | {message}"
    logger.info(message)
    return format_str


def log_warning(message: str, color: str = "yellow", apply_rich_text=False) -> str:
    if apply_rich_text:
        format_str = f"<span style = 'color:{color};white-space: pre' >{NOW()} | {'WARNING':<8} | {message}</span>"
    else:
        format_str = f"{NOW()} | {'WARNING':<8} | {message}"
    logger.warning(message)
    return format_str


def log_error(message: str, color: str = "red", apply_rich_text=False) -> str:
    if apply_rich_text:
        format_str = f"<span style = 'color:{color};white-space: pre' >{NOW()} | {'ERROR':<8} | {message}</span>"
    else:
        format_str = f"{NOW()} | {'ERROR':<8} | {message}"
    logger.error(message)
    return format_str


def format_log(message: str, color: str = "white", font_size: int = 20) -> str:
    format_str = f"<span style = 'color:{color};white-space: pre;font-size:{font_size}'>{message}</span>"
    return format_str


def show_center(widget: QWidget):
    """
    将窗口移动到屏幕中心并显示。
    首先获取当前屏幕的可用几何尺寸和窗口的当前尺寸，然后计算出窗口应移动到的位置，
    以便将窗口的中心定位到屏幕的中心。如果计算出的位置小于0，则将其设置为0，以避免窗口移出屏幕范围。
    最后，将窗口移动到计算出的位置，并显示窗口。
    :param widget: 需要移动并显示的窗口对象。
    """
    desktop = QApplication.primaryScreen().availableGeometry()
    cw = widget.frameGeometry().width()  # 获取窗口当前宽度
    ch = widget.frameGeometry().height()  # 获取窗口当前高度
    x = (desktop.width() - cw) // 2  # 使用整除以避免浮点数
    y = (desktop.height() - ch) // 2
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    widget.move(x, y)
    widget.show()


def copy_tree(src, dst: Path, symlinks=False, ignore=None):
    """
    复制文件夹及其内容。
    :param src: 源文件夹路径
    :param dst: 目标文件夹路径
    :param symlinks: 是否复制符号链接，默认为False
    :param ignore:
    :return: 函数 - 忽略某些文件或文件夹的函数，该函数应接受(source, names)作为参数并返回需要忽略的名称列表。
    """
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


def generate_color_map(classes: int) -> list[QColor]:
    """
    生成一个用于类的颜色映射列表。
    这个函数会为每个类生成一个随机的颜色，用QColor对象表示，这样在图形化处理时，
    不同的类可以对应不同的颜色，便于区分和可视化。

    :param classes: 需要生成颜色映射的类的数量。

    :return: 包含指定数量个QColor对象的列表，每个QColor对象代表一个随机颜色。
    """
    color_map = []
    for _ in range(classes):
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        color_map.append(QColor(r, g, b))
    return color_map


def generate_random_color() -> QColor:
    """
    生成一个随机颜色。
    :return 一个QColor对象，表示RGB颜色空间中的随机颜色。
    """
    # 生成0到255之间的随机整数，分别代表RGB分量
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)

    # 返回根据随机RGB分量创建的QColor对象
    return QColor(r, g, b)


def invert_color(color: QColor) -> QColor:
    """
    反转给定QColor对象的颜色。
    该函数通过取反QColor对象的RGB值来生成一个新的颜色，并返回该颜色的QColor对象。
    如果输入不是QColor对象，则抛出TypeError。
    :param color : 需要反转的颜色，必须是QColor对象。
    :return: 反转后的新颜色。
    """
    # 检查输入是否为QColor类型
    if not isinstance(color, QColor):
        raise TypeError("Expected QColor object, got {}".format(type(color)))

    try:
        # 获取原始颜色的RGB值
        red = color.red()
        green = color.green()
        blue = color.blue()

        # 对RGB值取反
        inverted_rgb = [255 - x for x in (red, green, blue)]

        # 创建一个新的QColor对象，包含取反后的RGB值
        inverted_color = QColor(*inverted_rgb)

        # 返回取反后的颜色
        return inverted_color
    except Exception as e:
        # 异常处理
        print(f"Error processing color: {e}")
        # 返回默认黑色作为错误处理结果
        return QColor(0, 0, 0)


def is_empty(folder_path: Path):
    """
    判断给定文件夹是否为空。
    该函数通过检查文件夹的内容来确定文件夹是否为空。它使用了Path对象的iterdir方法，
    该方法会生成文件夹内所有文件和子文件夹的迭代器。如果文件夹为空，iterdir不会返回任何内容，
    因此函数会返回True。反之，如果文件夹不为空，则返回False。
    :param folder_path: 一个Path对象，指向需要检查的文件夹。
    :return: 文件夹为空则返回True，否则返回False。
    """
    # 使用iterdir方法检查文件夹内容，并用not any构造表达式判断是否为空
    return not any(folder_path.iterdir())


def is_image(filename):
    """
    判断文件是否为图片
    :param filename: 文件名
    :return: 如果文件是图片，则返回True；否则返回False
    """
    try:
        # 尝试打开文件并验证其是否为图片
        with Image.open(filename) as img:
            img.verify()  # 验证图片是否完整
            return True
    except (IOError, SyntaxError):
        # 如果发生IO错误或语法错误，说明文件不是图片
        return False
