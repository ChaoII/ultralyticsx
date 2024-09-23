import time
from pathlib import Path

from PIL.ImageQt import QPixmap
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QBrush, QPolygonF

from common.utils import invert_color
from dataset.dataset_detail_widget.common.dataset_draw_thread_base import DatasetDrawThreadBase


class SegmentDatasetDrawThread(DatasetDrawThreadBase):
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
                        labels = [float(x) for x in line.split(" ")]
                        class_id = labels[0]
                        points = labels[1:]
                        polygon = QPolygonF()
                        for co in range(len(points) // 2):
                            x = points[2 * co] * pix.width()
                            y = points[2 * co + 1] * pix.height()
                            polygon.append(QPointF(x, y))

                        label = self.labels[int(class_id)]
                        color = self.color_list[int(class_id)]
                        inv_color = invert_color(color)
                        # 设置填充色
                        color.setAlpha(100)
                        # 设置边框颜色
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
                        # 绘制外接矩形
                        bounding_rect = polygon.boundingRect()
                        painter.drawRect(bounding_rect)  # 绘制矩形
                        # 设置填充色
                        painter.setBrush(QBrush(color))
                        # 绘制多边形
                        painter.drawPolygon(polygon)
                        fm = QFontMetrics(font)
                        # 文字填充色
                        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue())))
                        text_rect = QRectF(bounding_rect.x(), bounding_rect.y() - fm.height(),
                                           fm.boundingRect(label).width() + line_width, fm.height())
                        painter.drawRect(text_rect)

                        painter.setFont(font)
                        painter.setPen(QPen(inv_color))
                        painter.drawText(text_rect, label)
            painter.end()
            time.sleep(0.01)
            self.draw_one_image.emit(Path(row["image_path"]).name, pix)
