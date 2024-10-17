import enum
import math

from PySide6.QtCore import QPointF, QRectF, Qt, QLineF, QSizeF
from PySide6.QtGui import QPolygonF, QPainterPath, QPainter, QColor, QPen, QKeyEvent, QTransform
from PySide6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
from qfluentwidgets import themeColor

from annotation.core import DrawingStatus, drawing_status_manager


class ShapeType(enum.Enum):
    Rectangle = 0
    Polygon = 1
    Circle = 2
    Line = 3
    Point = 4


class ShapeItem(QGraphicsItem):
    class OperationType(enum.Enum):
        Move = 0
        Edit = 1

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
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton \
                and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if self.operation_type == RectangleItem.OperationType.Move:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.press_point = event.pos()
                self.press_points = self.points.copy()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.operation_type == RectangleItem.OperationType.Move and \
                drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            delta = event.pos() - self.press_point
            self.points.clear()
            for point in self.press_points:
                self.points.append(point + delta)
        else:
            self.points[self.hover_index] = event.pos()
        self.update_shape()
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and \
                drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = True
            self.update()

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
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

    def hoverLeaveEvent(self, event):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = False
            self.hover_index = -1
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()

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
        path.closeSubpath()
        return path

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
        return [self.rect.x() + self.rect.width() / 2,
                self.rect.y() + self.rect.height() / 2,
                self.rect.width(),
                self.rect.height()]

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
        if self.is_hover:
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
            corner_radius = self.corner_radius + 2
        if self.isSelected() :
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        painter.drawRect(self.rect)
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
