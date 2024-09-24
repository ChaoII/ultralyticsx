import time
from pathlib import Path

from PySide6.QtCore import Signal, QRect
from PySide6.QtGui import QPixmap, QPainter, QFont, QFontMetrics, QPen, QColor

from common.utils import invert_color
from ..common.dataset_draw_thread_base import DatasetDrawThreadBase


class ClassifyDatasetDrawThread(DatasetDrawThreadBase):
    draw_one_image = Signal(str, QPixmap)

    def __init__(self):
        super().__init__()

    def run(self):
        painter = QPainter()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, (index, row) in enumerate(self.image_paths.iterrows()):
            if i >= self.max_draw_num:
                break
            pix = QPixmap(row["image_path"])
            painter.begin(pix)
            if self.draw_labels:
                label = row["label"]
                # 绘制矩形
                line_width = 1
                # 设置填充色
                color = self.color_list[self.labels.index(label)]
                inv_color = invert_color(color)
                color.setAlpha(100)
                # 设置边框颜色
                painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
                # 获取字体大小
                font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
                font = QFont("Courier")
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
