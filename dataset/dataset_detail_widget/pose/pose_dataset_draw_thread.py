import time
from pathlib import Path

import numpy as np
from PIL.ImageQt import QPixmap
from PySide6.QtCore import QPointF, QRectF, Qt, QPoint
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
                        points = labels[2:]
                        key_points = []
                        for co in range(len(points) // 3):
                            x = int(points[2 * co] * pix.width())
                            y = int(points[2 * co + 1] * pix.height())
                            c = int(points[2 * co + 2])
                            key_points.append([x, y, c])

                        key_points = np.array(key_points)

                        for point_i, kpt in enumerate(key_points):
                            if kpt[2] <= 0.25:
                                continue
                            painter.drawEllipse(QPoint(kpt[0], kpt[1]), 3, 3)

                        for i, sk in enumerate(self.skeleton):
                            pos1 = (int(key_points[(sk[0] - 1), 0]), int(key_points[(sk[0] - 1), 1]))
                            pos2 = (int(key_points[(sk[1] - 1), 0]), int(key_points[(sk[1] - 1), 1]))

                            conf1 = key_points[(sk[0] - 1), 2]
                            conf2 = key_points[(sk[1] - 1), 2]
                            if conf1 < 0.25 or conf2 < 0.25:
                                continue
                            if pos1[0] % pix.width() == 0 or pos1[1] % pix.height() == 0 or pos1[0] < 0 or pos1[1] < 0:
                                continue
                            if pos2[0] % pix.width() == 0 or pos2[1] % pix.height() == 0 or pos2[0] < 0 or pos2[1] < 0:
                                continue
                            painter.drawLine(QPoint(pos1[0], pos1[1]), QPoint(pos2[0], pos2[1]))

            painter.end()
            time.sleep(0.01)
            self.draw_one_image.emit(Path(row["image_path"]).name, pix)
