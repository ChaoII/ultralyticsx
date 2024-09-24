import time
from pathlib import Path

import numpy as np
from PIL.ImageQt import QPixmap
from PySide6.QtCore import QPointF, QRectF, Qt, QPoint, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QBrush, QPolygonF

from common.utils import invert_color
from dataset.dataset_detail_widget.common.dataset_draw_thread_base import DatasetDrawThreadBase


# def kpts(kpts, shape=(640, 640), radius=5, kpt_line=True, conf_thres=0.25):
#     nkpt, ndim = kpts.shape
#     is_pose = nkpt == 17 and ndim in {2, 3}
#     kpt_line &= is_pose  # `kpt_line=True` for now only supports human pose plotting
#     for i, k in enumerate(kpts):
#         color_k = [int(x) for x in self.kpt_color[i]] if is_pose else colors(i)
#         x_coord, y_coord = k[0], k[1]
#         if x_coord % shape[1] != 0 and y_coord % shape[0] != 0:
#             if len(k) == 3:
#                 conf = k[2]
#                 if conf < conf_thres:
#                     continue
#             cv2.circle(self.im, (int(x_coord), int(y_coord)), radius, color_k, -1, lineType=cv2.LINE_AA)
#
#     if kpt_line:
#         ndim = kpts.shape[-1]
#         for i, sk in enumerate(self.skeleton):
#             pos1 = (int(kpts[(sk[0] - 1), 0]), int(kpts[(sk[0] - 1), 1]))
#             pos2 = (int(kpts[(sk[1] - 1), 0]), int(kpts[(sk[1] - 1), 1]))
#             if ndim == 3:
#                 conf1 = kpts[(sk[0] - 1), 2]
#                 conf2 = kpts[(sk[1] - 1), 2]
#                 if conf1 < conf_thres or conf2 < conf_thres:
#                     continue
#             if pos1[0] % shape[1] == 0 or pos1[1] % shape[0] == 0 or pos1[0] < 0 or pos1[1] < 0:
#                 continue
#             if pos2[0] % shape[1] == 0 or pos2[1] % shape[0] == 0 or pos2[0] < 0 or pos2[1] < 0:
#                 continue
#             cv2.line(self.im, pos1, pos2, [int(x) for x in self.limb_color[i]], thickness=2, lineType=cv2.LINE_AA)
#     if self.pil:
#         # Convert im back to PIL and update draw
#         self.fromarray(self.im)


class PoseDatasetDrawThread(DatasetDrawThreadBase):
    def __init__(self):
        super().__init__()
        self.skeleton = [
            [16, 14],
            [14, 12],
            [17, 15],
            [15, 13],
            [12, 13],
            [6, 12],
            [7, 13],
            [6, 7],
            [6, 8],
            [7, 9],
            [8, 10],
            [9, 11],
            [2, 3],
            [1, 2],
            [1, 3],
            [2, 4],
            [3, 5],
            [4, 6],
            [5, 7],
        ]
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
            ])
        self.limb_color = self.pose_palette[[9, 9, 9, 9, 7, 7, 7, 0, 0, 0, 0, 0, 16, 16, 16, 16, 16, 16, 16]]
        self.kpt_color = self.pose_palette[[16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9]]

    def run(self):
        painter = QPainter()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, (index, row) in enumerate(self.image_paths.iterrows()):
            if i >= self.max_draw_num:
                break
            pix = QPixmap(row["image_path"])
            width = pix.width()
            height = pix.height()
            painter.begin(pix)
            line_width = 2
            font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
            font = QFont("Courier")
            font.setPixelSize(font_size)
            if self.draw_labels:
                with open(row["label_path"], "r", encoding="utf8") as f:
                    lines = f.readlines()
                    for obj_i, line in enumerate(lines):
                        # [class, x_center, y_center, w, h, x1, y1, v1, x2, y2, v2... x17, y17, v17]
                        labels = [float(x) for x in line.split(" ")]
                        class_id = int(labels[0])
                        x_center = labels[1] * width
                        y_center = labels[2] * height
                        obj_width = int(labels[3] * width)
                        obj_height = int(labels[4] * height)
                        x = int(x_center - obj_width / 2)
                        y = int(y_center - obj_height / 2)

                        label = self.labels[class_id]
                        color = self.color_list[class_id]
                        inv_color = invert_color(color)
                        painter.setPen(QPen(color, line_width))
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        painter.drawRect(x, y, obj_width, obj_height)

                        # 获取字体大小
                        fm = QFontMetrics(font)
                        # 文字填充色
                        painter.setBrush(QBrush(color))
                        text_rect = QRect(x, y - fm.height(), fm.boundingRect(label).width() + line_width, fm.height())
                        painter.drawRect(text_rect)
                        # 绘制文字
                        painter.setFont(font)
                        painter.setPen(QPen(inv_color))
                        painter.drawText(text_rect, label)

                        points = labels[5:]
                        key_points = []
                        for co in range(len(points) // 3):
                            x = int(points[co * 3] * width)
                            y = int(points[co * 3 + 1] * height)
                            c = int(points[co * 3 + 2])
                            key_points.append([x, y, c])

                        key_points = np.array(key_points)
                        # 绘制关键点
                        for point_i, kpt in enumerate(key_points):
                            if kpt[2] <= 0.25:
                                continue
                            color_k = [int(x) for x in self.kpt_color[point_i]]
                            painter.setPen(QPen(QColor(*color_k), line_width))
                            painter.setBrush(QBrush(QColor(*color_k)))
                            painter.drawEllipse(QPoint(kpt[0], kpt[1]), 3, 3)
                        # 绘制关键点连线
                        for sk_i, sk in enumerate(self.skeleton):
                            color_line = [int(x) for x in self.limb_color[sk_i]]
                            painter.setPen(QPen(QColor(*color_line), line_width))
                            pos1 = (int(key_points[(sk[0] - 1), 0]), int(key_points[(sk[0] - 1), 1]))
                            pos2 = (int(key_points[(sk[1] - 1), 0]), int(key_points[(sk[1] - 1), 1]))

                            conf1 = key_points[(sk[0] - 1), 2]
                            conf2 = key_points[(sk[1] - 1), 2]
                            if conf1 < 0.25 or conf2 < 0.25:
                                continue
                            if pos1[0] % width == 0 or pos1[1] % height == 0 or pos1[0] < 0 or pos1[1] < 0:
                                continue
                            if pos2[0] % width == 0 or pos2[1] % height == 0 or pos2[0] < 0 or pos2[1] < 0:
                                continue
                            painter.drawLine(QPoint(pos1[0], pos1[1]), QPoint(pos2[0], pos2[1]))

            painter.end()
            time.sleep(0.01)
            self.draw_one_image.emit(Path(row["image_path"]).name, pix)
