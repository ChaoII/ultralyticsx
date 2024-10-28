import enum
import math

from PySide6.QtCore import QPointF, QRectF, Qt, QLineF, QSizeF
from PySide6.QtGui import QPolygonF, QPainterPath, QPainter, QColor, QPen, QKeyEvent, QTransform, QPainterPathStroker, \
    QPixmap, QCursor
from PySide6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
from qfluentwidgets import themeColor

from annotation.core import DrawingStatus, drawing_status_manager


class ShapeType(enum.Enum):
    Rectangle = 0
    RotatedRectangle = 1
    Polygon = 2
    Circle = 3
    Line = 4
    Point = 5


class ShapeItem(QGraphicsItem):
    class OperationType(enum.Enum):
        Move = 0
        Edit = 1
        Rotate = 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.operation_type = ShapeItem.OperationType.Move
        self.color = themeColor()
        self.is_hover = False
        self.corner_radius = 4
        self.hover_index = -1
        self.points: list[QPointF] = []
        # 记录鼠标点击时所在的点
        self.press_point = QPointF()
        self.press_points: list[QPointF] = []
        self._annotation_id = ""
        self._annotation = ""
        self._is_drawing_history = False

    def set_is_drawing_history(self, is_drawing_history: bool):
        self._is_drawing_history = is_drawing_history

    def get_is_drawing_history(self) -> bool:
        return self._is_drawing_history

    def set_id(self, annotation_id: str):
        self._annotation_id = annotation_id

    def get_id(self) -> str:
        return self._annotation_id

    def set_annotation(self, annotation: str):
        self._annotation = annotation

    def get_annotation(self) -> str:
        return self._annotation

    @staticmethod
    def get_shape_type() -> ShapeType:
        raise NotImplementedError

    def update_points(self, points: list[QPointF]):
        self.points = points
        self.update_shape()

    def set_color(self, color: QColor):
        self.color = color

    def update_shape(self):
        raise NotImplementedError

    def get_shape_data(self) -> list:
        raise NotImplementedError

    def set_hover(self, is_hover: bool):
        self.is_hover = is_hover

    def move_by(self, offset: QPointF):
        for i in range(len(self.points)):
            self.points[i] = self.points[i] + offset
        self.update_shape()
        self.update()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        self.prepareGeometryChange()
        if event.button() == Qt.MouseButton.LeftButton \
                and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if self.operation_type == RectangleItem.OperationType.Move:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.press_point = event.pos()
                self.press_points = self.points.copy()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.prepareGeometryChange()
        if drawing_status_manager.get_drawing_status() == DrawingStatus.Draw:
            return
        if self.operation_type == RectangleItem.OperationType.Move:
            delta = event.pos() - self.press_point
            self.points.clear()
            for point in self.press_points:
                self.points.append(point + delta)
        elif self.operation_type == ShapeItem.OperationType.Edit:
            self.points[self.hover_index] = event.pos()
        else:
            pass
        self.update_shape()
        self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.prepareGeometryChange()
        if event.button() == Qt.MouseButton.LeftButton and \
                drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.prepareGeometryChange()
            self.is_hover = True
            self.update()
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.prepareGeometryChange()
            pad = [-8, -8, 8, 8]
            is_point_hover = False
            for index, point in enumerate(self.points):
                if QRectF(point, QSizeF(1, 1)).adjusted(*pad).contains(event.pos()):
                    self.hover_index = index
                    is_point_hover = True
                    break
            if is_point_hover:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                self.operation_type = RectangleItem.OperationType.Edit
            else:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                self.operation_type = RectangleItem.OperationType.Move
                self.hover_index = -1
            self.update()
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.prepareGeometryChange()
            self.is_hover = False
            self.hover_index = -1
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
        super().hoverLeaveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.move_by(QPointF(-1, 0))
        if event.key() == Qt.Key.Key_Right:
            self.move_by(QPointF(1, 0))
        if event.key() == Qt.Key.Key_Up:
            self.move_by(QPointF(0, -1))
        if event.key() == Qt.Key.Key_Down:
            self.move_by(QPointF(0, 1))
        super().keyPressEvent(event)


class PolygonItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.operation_type = RectangleItem.OperationType.Move
        self.polygon = QPolygonF()
        # 记录鼠标按下时的多边形
        self.first_point_hover = False

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Polygon

    def update_shape(self):
        polygon = QPolygonF()
        for point in self.points:
            polygon.append(point)
        self.polygon = polygon

    def get_shape_data(self):
        result = []
        for point in self.points:
            result.append(point.x())

    def boundingRect(self) -> QRectF:
        rect = self.polygon.boundingRect()
        return rect.adjusted(-self.corner_radius, -self.corner_radius,
                             self.corner_radius, self.corner_radius)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addPolygon(self.polygon)
        # 创建一个描边工具
        stroker = QPainterPathStroker()
        stroker.setWidth(2 * 10)  # 描边宽度为 2 * pixels
        # 生成扩大的路径
        expanded_path = stroker.createStroke(path)
        expanded_path.addPath(path)  # 将原始路径添加到扩大的路径中
        # 获取扩大的多边形
        expanded_polygon = expanded_path.toFillPolygon()
        p1 = QPainterPath()
        p1.addPolygon(expanded_polygon)
        p1.closeSubpath()
        return p1

    def set_first_point_hover(self, first_point_hover: bool):
        self.first_point_hover = first_point_hover

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        brush_color = QColor(self.color)
        corner_radius = self.corner_radius

        if self.is_hover:
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
            corner_radius = self.corner_radius + 2
        if self.isSelected():
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        painter.drawPolygon(self.polygon)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index or (index == 0 and self.first_point_hover):
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, corner_radius, corner_radius)


class RectangleItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.rect = QRectF()

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Rectangle

    def update_shape(self):
        x1 = min(self.points[0].x(), self.points[1].x())
        y1 = min(self.points[0].y(), self.points[1].y())
        x2 = max(self.points[0].x(), self.points[1].x())
        y2 = max(self.points[0].y(), self.points[1].y())
        self.rect = QRectF(x1, y1, x2 - x1, y2 - y1)

    def get_shape_data(self):
        # x_center, y_center, w, h
        x_center = self.rect.center().x()
        y_center = self.rect.center().y()
        w = self.rect.width()
        h = self.rect.height()
        return [x_center, y_center, w, h]

    def boundingRect(self) -> QRectF:
        return self.rect.adjusted(-self.corner_radius, -self.corner_radius,
                                  self.corner_radius, self.corner_radius)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.rect.adjusted(-self.corner_radius, -self.corner_radius,
                                        self.corner_radius, self.corner_radius))
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        brush_color = QColor(self.color)
        corner_radius = self.corner_radius
        if self.isSelected():
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        if self.is_hover or self.isSelected():
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
            corner_radius = self.corner_radius + 2
        painter.drawRect(self.rect)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, corner_radius, corner_radius)


class RotatedRectangleItem(ShapeItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.polygon = QPolygonF()
        self.angle = 0
        self.w = 0
        self.h = 0
        self.direction = 0

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.RotatedRectangle

    @staticmethod
    def distance_point_to_line(point: QPointF, line: QLineF) -> float:
        x1, y1 = line.p1().x(), line.p1().y()
        x2, y2 = line.p2().x(), line.p2().y()
        x3, y3 = point.x(), point.y()

        # 计算直线方程的系数
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        # 计算点到直线的距离
        numerator = abs(A * x3 + B * y3 + C)
        denominator = math.sqrt(A ** 2 + B ** 2)
        distance = numerator / denominator

        return distance

    @staticmethod
    def is_point_left_of_line(point: QPointF, line: QLineF) -> bool:
        x1, y1 = line.p1().x(), line.p1().y()
        x2, y2 = line.p2().x(), line.p2().y()
        x3, y3 = point.x(), point.y()

        # 计算向量 v1 和 v2
        v1_x, v1_y = x2 - x1, y2 - y1
        v2_x, v2_y = x3 - x1, y3 - y1

        # 计算叉乘
        cross_product = v1_x * v2_y - v1_y * v2_x

        # 判断点的位置
        return cross_product > 0

    def update_shape(self):
        if len(self.points) == 2:
            p1 = self.points[0]
            p2 = self.points[1]
            p3_ = p2
            p4_ = p1
        elif len(self.points) == 3:
            p1 = self.points[0]
            p2 = self.points[1]
            p3 = self.points[2]
            l1 = QLineF(p1, p2)
            self.w = l1.length()
            self.h = self.distance_point_to_line(p3, l1)
            self.angle = l1.angle()
            p_delta = QPointF(self.h * math.sin(math.radians(self.angle)),
                              self.h * math.cos(math.radians(self.angle)))
            if self.is_point_left_of_line(p3, l1):
                p3_ = p2 + p_delta
                p4_ = p1 + p_delta
            else:
                p3_ = p2 - p_delta
                p4_ = p1 - p_delta
            # 让控制点吸附在矩形边的中间
            self.points[2] = (QPointF((p3_.x() + p4_.x()) / 2, (p3_.y() + p4_.y()) / 2))
        else:
            return
        self.polygon = QPolygonF([p1, p2, p3_, p4_])

    def get_shape_data(self):
        data = []
        for point in self.polygon.toList():
            data += [point.x(), point.y()]
        return data

    def boundingRect(self) -> QRectF:
        return self.polygon.boundingRect().adjusted(-self.corner_radius, -self.corner_radius,
                                                    self.corner_radius, self.corner_radius)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addPolygon(self.polygon)
        # 创建一个描边工具
        stroker = QPainterPathStroker()
        stroker.setWidth(2 * 10)  # 描边宽度为 2 * pixels
        # 生成扩大的路径
        expanded_path = stroker.createStroke(path)
        expanded_path.addPath(path)  # 将原始路径添加到扩大的路径中
        # 获取扩大的多边形
        expanded_polygon = expanded_path.toFillPolygon()
        p1 = QPainterPath()
        p1.addPolygon(expanded_polygon)
        p1.closeSubpath()
        return p1

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        brush_color = QColor(self.color)
        corner_radius = self.corner_radius
        if self.isSelected():
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        if self.is_hover or self.isSelected():
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
            corner_radius = self.corner_radius + 2
        painter.drawPolygon(self.polygon)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, corner_radius, corner_radius)


class CircleItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Circle

    def update_shape(self):
        pass

    def get_shape_data(self):
        # x_center, y_center, r
        radius = self.calculate_radius()
        return [self.points[0].x(), self.points[0].y(), radius]

    def calculate_radius(self):
        d = self.points[0] - self.points[1]
        return math.sqrt(d.x() ** 2 + d.y() ** 2)

    def boundingRect(self) -> QRectF:
        center = self.points[0]
        radius = self.calculate_radius()
        x = center.x() - radius
        y = center.y() - radius
        w = radius * 2
        h = radius * 2
        rect = QRectF(x, y, w, h)
        return rect.adjusted(-self.corner_radius, -self.corner_radius,
                             self.corner_radius, self.corner_radius)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        radius = self.calculate_radius() + 8
        path.addEllipse(self.points[0], radius, radius)
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        brush_color = QColor(self.color)
        corner_radius = self.corner_radius
        if self.is_hover:
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
            corner_radius = self.corner_radius + 2
        if self.isSelected():
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        radius = self.calculate_radius()
        painter.drawEllipse(self.points[0], radius, radius)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, corner_radius, corner_radius)


class PointItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.operation_type = RectangleItem.OperationType.Move
        # 记录鼠标按下时的矩形快照
        self.cur_press_point = [QPointF(0, 0)]

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Point

    def update_shape(self):
        pass

    def get_shape_data(self):
        # x, y
        return [self.points[0].x(), self.points[0].y()]

    def boundingRect(self) -> QRectF:
        rect = QRectF(self.points[0], QSizeF(1, 1))
        return rect.adjusted(-self.corner_radius, -self.corner_radius,
                             self.corner_radius, self.corner_radius)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self.points[0], self.corner_radius * 2, self.corner_radius * 2)
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(self.color)
        if self.is_hover:
            painter.drawEllipse(self.points[0], self.corner_radius * 2, self.corner_radius * 2)
        else:
            painter.drawEllipse(self.points[0], self.corner_radius, self.corner_radius)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.points[self.hover_index] = event.pos()
        self.update()
        super().mouseMoveEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.update()


class LineItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.line = QLineF()

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Line

    def update_shape(self):
        self.line = QLineF(self.points[0], self.points[1])

    def get_shape_data(self):
        return [self.line.x1(), self.line.y1(), self.line.x2(), self.line.y2()]

    def boundingRect(self) -> QRectF:
        x1 = min(self.points[0].x(), self.points[1].x())
        y1 = min(self.points[0].y(), self.points[1].y())
        x2 = max(self.points[0].x(), self.points[1].x())
        y2 = max(self.points[0].y(), self.points[1].y())
        rect = QRectF(QPointF(x1, y1), QPointF(x2, y2))
        return rect.adjusted(-self.corner_radius, -self.corner_radius,
                             self.corner_radius, self.corner_radius)

    def shape(self) -> QPainterPath:
        angle = self.line.angle()
        length = self.line.length()
        margin = 20  # 容差范围
        center = self.line.center()
        x1 = center.x() - length / 2 - 10
        y1 = center.y() - margin / 2
        x2 = center.x() + length / 2 + 10
        y2 = center.y() + margin / 2

        p1 = QPointF(x1, y1)
        p2 = QPointF(x2, y1)
        p3 = QPointF(x2, y2)
        p4 = QPointF(x1, y2)

        polygon = QPolygonF()
        polygon.append(p1)
        polygon.append(p2)
        polygon.append(p3)
        polygon.append(p4)
        polygon.append(p1)

        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(-angle)
        transform.translate(-center.x(), -center.y())
        r_polygon = transform.map(polygon)
        path = QPainterPath()
        path.addPolygon(r_polygon)
        path.closeSubpath()
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        corner_radius = self.corner_radius
        if self.is_hover:
            painter.setPen(QPen(self.color, 2, Qt.PenStyle.SolidLine))
            corner_radius = self.corner_radius + 2
        if self.isSelected() and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            painter.setPen(QPen(self.color, 2, Qt.PenStyle.DashLine))
        painter.drawLine(self.line)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, corner_radius, corner_radius)


class ImageItem(QGraphicsItem):

    def __init__(self, pix, parent=None):
        super().__init__(parent)
        self.pix = pix

    def set_pixmap(self, pix: QPixmap):
        self.pix = pix

    def boundingRect(self) -> QRectF:
        rect = self.pix.rect().toRectF()
        return rect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.pix.rect())

        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.pix)
