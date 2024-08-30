import time
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QThread, Signal, QRect
from PySide6.QtGui import QPixmap, QPainter, QFont, QFontMetrics, QPen, QColor

from common.utils import generate_color_map, invert_color


class DatasetDrawThread(QThread):
    draw_one_image = Signal(str, QPixmap)

    def __init__(self):
        super().__init__()
        self.max_draw_num = 50
        self.draw_labels = False
        self.color_list = []
        self.labels = []
        self.image_paths: pd.DataFrame = pd.DataFrame()

    def set_dataset_path(self, dataset_paths: list[Path]):
        self.image_paths = dataset_paths

    def set_dataset_label(self, labels):
        self.labels = list(labels)
        self.color_list = generate_color_map(len(labels))

    def set_draw_labels_status(self, status: bool):
        self.draw_labels = status

    def set_max_draw_nums(self, max_draw_num: int):
        self.max_draw_num = max_draw_num

    def run(self):
        for i, (index, row) in enumerate(self.image_paths.iterrows()):
            if i >= self.max_draw_num:
                break
            pix = QPixmap(row["image_path"])
            if self.draw_labels:
                label = row["label"]
                # 绘制矩形
                painter = QPainter(pix)
                line_width = min(pix.width(), pix.height()) // 50
                # 设置填充色
                color = self.color_list[self.labels.index(label)]
                inv_color = invert_color(color)
                color.setAlpha(100)
                # 设置边框颜色
                painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
                # 获取字体大小
                font_size = min(pix.width(), pix.height()) // 10  # 假设文字大小是窗口大小的10%
                font = QFont("Microsoft YaHei UI")
                font.setPixelSize(font_size)
                fm = QFontMetrics(font)

                # 文字填充色
                painter.setBrush(color)
                new_rect = QRect(5, 5, fm.boundingRect(label).width() + line_width, fm.height())
                painter.drawRect(new_rect)
                painter.setFont(font)
                painter.setPen(QPen(inv_color))
                painter.drawText(new_rect, label)
                painter.end()
            time.sleep(0.01)
            self.draw_one_image.emit(Path(row["image_path"]).name, pix)
