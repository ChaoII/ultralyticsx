import time
from pathlib import Path

from PIL.ImageQt import QPixmap
from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QBrush

from common.utils.utils import invert_color
from ..common.dataset_draw_thread_base import DatasetDrawThreadBase


class DetectionDatasetDrawThread(DatasetDrawThreadBase):

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
            line_width = 1
            font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
            font = QFont("Courier")
            font.setPixelSize(font_size)
            if self.draw_labels:
                with open(row["label_path"], "r", encoding="utf8") as f:
                    lines = f.readlines()
                    for line in lines:
                        class_id, x_center, y_center, width, height = [float(x) for x in line.split(" ")]
                        x = (x_center - width / 2) * pix.width()
                        y = (y_center - height / 2) * pix.height()
                        width_ = width * pix.width()
                        height_ = height * pix.height()

                        label = self.labels[int(class_id)]
                        color = self.color_list[int(class_id)]
                        inv_color = invert_color(color)
                        # 设置填充色
                        color.setAlpha(100)
                        painter.setBrush(QBrush(color))
                        # 设置边框颜色
                        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
                        painter.drawRect(x, y, width_, height_)  # 绘制矩形
                        # 获取字体大小
                        fm = QFontMetrics(font)
                        # 文字填充色
                        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue())))
                        text_rect = QRect(x, y - fm.height(), fm.boundingRect(label).width() + line_width, fm.height())
                        painter.drawRect(text_rect)

                        painter.setFont(font)
                        painter.setPen(QPen(inv_color))
                        painter.drawText(text_rect, label)
            painter.end()
            time.sleep(0.01)
            self.draw_one_image.emit(Path(row["image_path"]).name, pix)
