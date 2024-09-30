import numpy as np
from PySide6.QtCore import QRect, QRectF, QPointF, QPoint
from PySide6.QtGui import QColor, QPen, QPainter, QImage, QFont, QFontMetrics, QBrush, QPolygonF, Qt

from common.utils.utils import generate_color_map, invert_color, generate_random_color

skeleton = [
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
pose_palette = np.array(
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
limb_color = pose_palette[[9, 9, 9, 9, 7, 7, 7, 0, 0, 0, 0, 0, 16, 16, 16, 16, 16, 16, 16]]
kpt_color = pose_palette[[16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9]]


def draw_classify_result(pix: QImage, label: str, line_width: int = 1):
    painter = QPainter()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.begin(pix)
    # 设置填充色
    color = generate_random_color()
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
    text_rect = QRect(5, 5, fm.boundingRect(label).width() + line_width, fm.height())
    painter.drawRect(text_rect)
    painter.setFont(font)
    painter.setPen(QPen(inv_color))
    painter.drawText(text_rect, label)
    painter.end()


def draw_detect_result(pix: QImage, labels_name_map: dict, boxes: list, line_width: int = 1):
    painter = QPainter()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.begin(pix)
    font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
    font = QFont("Courier")
    font.setPixelSize(font_size)
    colors_map = generate_color_map(len(labels_name_map.keys()))
    for box in boxes:
        x1, y1, x2, y2, conf, class_id = box
        label = labels_name_map[int(class_id)]
        color = colors_map[int(class_id)]
        inv_color = invert_color(color)
        # 设置填充色
        color.setAlpha(100)
        painter.setBrush(QBrush(color))
        # 设置边框颜色
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
        painter.drawRect(QRectF(QPointF(x1, y1), QPointF(x2, y2)))  # 绘制矩形
        # 获取字体大小
        fm = QFontMetrics(font)
        # 文字填充色
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue())))
        txt = f"{label}_{conf:.2f}"
        text_rect = QRect(x1, y1 - fm.height(), fm.boundingRect(txt).width() + line_width,
                          fm.height())
        painter.drawRect(text_rect)
        painter.setFont(font)
        painter.setPen(QPen(inv_color))
        painter.drawText(text_rect, txt)
    painter.end()


def draw_segment_result(pix: QImage, labels_name_map: dict, boxes: list, masks: list, line_width: int = 1):
    painter = QPainter()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.begin(pix)
    font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
    font = QFont("Courier")
    font.setPixelSize(font_size)
    colors_map = generate_color_map(len(labels_name_map.keys()))
    for box, mask in zip(boxes, masks):
        x1, y1, x2, y2, conf, class_id = box
        label = labels_name_map[int(class_id)]
        color = colors_map[int(class_id)]
        polygon = QPolygonF()
        for x, y in mask:
            polygon.append(QPointF(x, y))
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
        txt = f"{label}_{conf:.2f}"
        text_rect = QRectF(bounding_rect.x(), bounding_rect.y() - fm.height(),
                           fm.boundingRect(txt).width() + line_width, fm.height())
        painter.drawRect(text_rect)
        painter.setFont(font)
        painter.setPen(QPen(inv_color))
        painter.drawText(text_rect, txt)
    painter.end()


def draw_obb_result(pix: QImage, labels_name_map: dict, classes: list, confs: list, boxes: list, line_width: int = 1):
    painter = QPainter()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.begin(pix)
    font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
    font = QFont("Courier")
    font.setPixelSize(font_size)
    colors_map = generate_color_map(len(labels_name_map.keys()))
    for cls, conf, box in zip(classes, confs, boxes):
        polygon = QPolygonF()
        for x, y in box:
            polygon.append(QPointF(x, y))
        label = labels_name_map[int(cls)]
        color = colors_map[int(cls)]
        inv_color = invert_color(color)
        # 设置填充色
        color.setAlpha(100)
        painter.setBrush(QBrush(color))
        # 设置边框颜色
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue()), line_width))  # 设置画笔颜色和宽度
        painter.drawPolygon(polygon)  # 绘制旋转矩形
        # 获取字体大小
        fm = QFontMetrics(font)
        # 文字填充色
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue())))
        txt = f"{label}_{conf:.2f}"
        text_rect = QRect(box[0][0], box[0][1] - fm.height(),
                          fm.boundingRect(txt).width() + line_width, fm.height())
        painter.drawRect(text_rect)
        painter.setFont(font)
        painter.setPen(QPen(inv_color))
        painter.drawText(text_rect, txt)
    painter.end()


def draw_pose_result(pix: QImage, labels_name_map: dict, boxes: list, key_points: list, line_width: int = 1):
    painter = QPainter()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.begin(pix)
    font_size = min(pix.width(), pix.height()) // 20  # 假设文字大小是窗口大小的10%
    font = QFont("Courier")
    font.setPixelSize(font_size)
    colors_map = generate_color_map(len(labels_name_map.keys()))
    for box, kpts in zip(boxes, key_points):
        kpts = np.array(kpts)
        # [class, x_center, y_center, w, h, x1, y1, v1, x2, y2, v2... x17, y17, v17]
        x1, y1, x2, y2, conf, class_id = box
        label = labels_name_map[int(class_id)]
        color = colors_map[int(class_id)]
        inv_color = invert_color(color)
        painter.setPen(QPen(color, line_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))
        # 获取字体大小
        fm = QFontMetrics(font)
        # 文字填充色
        painter.setBrush(QBrush(color))
        text_rect = QRect(x1, y1 - fm.height(), fm.boundingRect(label).width() + line_width, fm.height())
        painter.drawRect(text_rect)
        # # 绘制文字
        painter.setFont(font)
        painter.setPen(QPen(inv_color))
        painter.drawText(text_rect, label)
        # 绘制关键点
        for point_i, kpt in enumerate(kpts):
            if kpt[2] <= 0.25:
                continue
            color_k = [int(x) for x in kpt_color[point_i]]
            painter.setPen(QPen(QColor(*color_k), line_width))
            painter.setBrush(QBrush(QColor(*color_k)))
            painter.drawEllipse(QPoint(kpt[0], kpt[1]), 3, 3)
        # 绘制关键点连线
        for sk_i, sk in enumerate(skeleton):
            color_line = [int(x) for x in limb_color[sk_i]]
            painter.setPen(QPen(QColor(*color_line), line_width))
            pos1 = (int(kpts[(sk[0] - 1), 0]), int(kpts[(sk[0] - 1), 1]))
            pos2 = (int(kpts[(sk[1] - 1), 0]), int(kpts[(sk[1] - 1), 1]))
            conf1 = kpts[(sk[0] - 1), 2]
            conf2 = kpts[(sk[1] - 1), 2]
            if conf1 < 0.25 or conf2 < 0.25:
                continue
            if pos1[0] == 0 or pos1[1] == 0 or pos1[0] < 0 or pos1[1] < 0:
                continue
            if pos2[0] == 0 or pos2[1] == 0 or pos2[0] < 0 or pos2[1] < 0:
                continue
            painter.drawLine(QPoint(pos1[0], pos1[1]), QPoint(pos2[0], pos2[1]))
