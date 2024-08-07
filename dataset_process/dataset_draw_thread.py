import os
from pathlib import Path

import numpy as np
from PySide6.QtCore import QSize, Signal, QRect, QThread
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont, QBrush, QFontMetrics
from .utils import plot_labels
from utils.utils import *

SMALL = QSize(60, 60)
MEDIUM = QSize(120, 120)
LARGE = QSize(200, 200)

RESOLUTIONS = [SMALL, MEDIUM, LARGE]
DATASET_TYPES = ["train", "val", "test"]


class DatasetDrawThread(QThread):
    draw_labels_finished = Signal(str, QPixmap)

    def __init__(self, labels_map: dict | None = None):
        super().__init__()
        self.max_draw_num = 50
        self.image_dir: Path | None = None
        self.annotation_dir = None
        self.draw_labels = False
        self.labels_map = labels_map
        self.color_map = None

    def set_dataset_path(self, dataset_path: Path, annotation_path: Path):
        self.image_dir = dataset_path
        self.annotation_dir = annotation_path

    def set_draw_labels_status(self, status: bool):
        self.draw_labels = status

    def set_labels_map(self, labels_map: dict):
        self.labels_map = labels_map
        self.color_map = generate_color_map(len(labels_map))

    def set_max_draw_nums(self, max_draw_num: int):
        self.max_draw_num = max_draw_num

    def run(self):
        cls = []
        boxes = []
        for index, filename in enumerate(os.listdir(self.image_dir.resolve().as_posix())):
            if index >= self.max_draw_num:
                break
            file_path = self.image_dir / filename
            pix = QPixmap(file_path.resolve().as_posix())
            if self.draw_labels:
                annotation_file = (self.annotation_dir / filename.split(".")[0]).resolve().as_posix() + ".txt"
                with open(annotation_file, "r", encoding="utf8") as f:
                    lines = f.readlines()
                    for line in lines:
                        painter = QPainter(pix)
                        category_id, x_center, y_center, width, height = [float(x) for x in line.split(" ")]
                        x = (x_center - width / 2) * pix.width()
                        y = (y_center - height / 2) * pix.height()
                        width_ = width * pix.width()
                        height_ = height * pix.height()
                        label = self.labels_map[int(category_id)]
                        color = self.color_map[int(category_id)]
                        inv_color = invert_color(color)
                        # 绘制矩形
                        line_width = min(width_, height_) // 50
                        # 设置填充色
                        color.setAlpha(100)
                        painter.setBrush(QBrush(color))
                        # 设置边框颜色
                        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
                        painter.drawRect(x, y, width_, height_)  # 绘制矩形
                        # 获取字体大小
                        font_size = min(width_, height_) // 10  # 假设文字大小是窗口大小的10%
                        font = QFont("Microsoft YaHei UI")
                        font.setPixelSize(font_size)
                        fm = QFontMetrics(font)

                        # 文字填充色
                        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue())))
                        new_rect = QRect(x, y - fm.height(), fm.boundingRect(label).width(), fm.height())
                        painter.drawRect(new_rect)

                        painter.setFont(font)
                        painter.setPen(QPen(inv_color))
                        painter.drawText(new_rect, label)
                        painter.end()

                        cls.append(category_id)
                        boxes.append([x_center, y_center, width, height])
            self.draw_labels_finished.emit(filename, pix)
        plot_labels(np.array(boxes), np.array(cls), self.labels_map, self.image_dir.parent.parent)
