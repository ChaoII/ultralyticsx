import enum
import math

from PySide6.QtCore import QPointF, QRectF, Qt, QLineF
from PySide6.QtGui import QPolygonF, QPainterPath, QPainter
from PySide6.QtWidgets import QGraphicsItem


class ShapeType(enum.Enum):
    Rectangle = 0
    Polygon = 1
    Circle = 2
    Line = 3
    Point = 4


class PolygonLineItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.polygon_points = QPolygonF()
        self.close_status = False
        self.first_point_hover = False
        self.corner_radius = 8

    def set_polygon(self, polygon: QPolygonF):
        self.polygon_points = polygon

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addPolygon(self.polygon_points)
        return path

    def set_first_point_hover(self, first_point_hover: bool):
        self.first_point_hover = first_point_hover

    def boundingRect(self) -> QRectF:
        if self.polygon_points.isEmpty():
            return QRectF()
        return self.polygon_points.boundingRect()

    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.GlobalColor.blue)
        painter.setPen(Qt.GlobalColor.blue)
        path = QPainterPath()
        path.moveTo(self.polygon_points.value(0))
        for index, point in enumerate(self.polygon_points.toList()):
            painter.drawEllipse(point, self.corner_radius, self.corner_radius)
            if index == 0 and self.first_point_hover:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(1, self.polygon_points.size()):
            path.lineTo(self.polygon_points.value(i))
        painter.drawPath(path)


class RectangleItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.rect = QRectF()
        self.color = Qt.GlobalColor.red
        self.border_color = Qt.GlobalColor.black
        self.border_width = 2
        self.is_hover = False
        self.is_selected = False
        self.is_dragging = False
        self.is_moving = False
        self.corner_radius = 8

    def set_rect(self, rect: QRectF):
        self.rect = rect

    def boundingRect(self) -> QRectF:
        p1 = self.rect.topLeft()
        p2 = self.rect.bottomRight()

        x1 = min(p1.x(), p2.x())
        y1 = min(p1.y(), p2.y())
        x2 = max(p1.x(), p2.x())
        y2 = max(p1.y(), p2.y())
        rect = QRectF(x1, y1, x2 - x1, y2 - y1)

        return rect.adjusted(self.corner_radius / 2, self.corner_radius / 2,
                             self.corner_radius / 2, self.corner_radius / 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.rect)
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.border_color)
        painter.setBrush(self.color)
        if self.is_hover:
            painter.setPen(Qt.GlobalColor.blue)
        if self.is_selected:
            painter.setPen(Qt.GlobalColor.blue)
        painter.drawRect(self.rect)
        painter.drawEllipse(self.rect.topLeft(), self.corner_radius, self.corner_radius)
        painter.drawEllipse(self.rect.bottomRight(), self.corner_radius, self.corner_radius)


class CircleItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.points = [QPointF(), QPointF()]
        self.color = Qt.GlobalColor.red
        self.border_color = Qt.GlobalColor.black
        self.border_width = 2
        self.is_hover = False
        self.is_selected = False
        self.is_dragging = False
        self.is_moving = False
        self.corner_radius = 8

    def set_points(self, points: [QPointF]):
        self.points = points

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
        return rect.adjusted(self.corner_radius / 2, self.corner_radius / 2,
                             self.corner_radius / 2, self.corner_radius / 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        radius = self.calculate_radius()
        path.addEllipse(self.points[0], radius, radius)
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.border_color)
        painter.setBrush(self.color)
        if self.is_hover:
            painter.setPen(Qt.GlobalColor.blue)
        if self.is_selected:
            painter.setPen(Qt.GlobalColor.blue)

        radius = self.calculate_radius()
        painter.drawEllipse(self.points[0], radius, radius)
        painter.drawEllipse(self.points[0], self.corner_radius, self.corner_radius)
        painter.drawEllipse(self.points[1], self.corner_radius, self.corner_radius)


class PointItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.point = QPointF()
        self.color = Qt.GlobalColor.red
        self.border_color = Qt.GlobalColor.black
        self.border_width = 2
        self.is_hover = False
        self.is_selected = False
        self.is_dragging = False
        self.is_moving = False
        self.corner_radius = 8

    def set_point(self, point: QPointF):
        self.point = point

    def boundingRect(self) -> QRectF:
        center = self.point
        x = center.x() - self.corner_radius
        y = center.y() - self.corner_radius
        w = self.corner_radius * 2
        h = self.corner_radius * 2
        return QRectF(x, y, w, h)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.border_color)
        painter.setBrush(self.color)
        if self.is_hover:
            painter.setPen(Qt.GlobalColor.blue)
        if self.is_selected:
            painter.setPen(Qt.GlobalColor.blue)
        painter.drawEllipse(self.point, self.corner_radius, self.corner_radius)


class LineItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.line = QLineF()
        self.color = Qt.GlobalColor.red
        self.border_color = Qt.GlobalColor.black
        self.border_width = 2
        self.is_hover = False
        self.is_selected = False
        self.is_dragging = False
        self.is_moving = False
        self.corner_radius = 8

    def set_line(self, line: QLineF):
        self.line = line

    def boundingRect(self) -> QRectF:

        x1 = min(self.line.x1(), self.line.x2())
        y1 = min(self.line.y1(), self.line.y2())
        x2 = max(self.line.x1(), self.line.x2())
        y2 = max(self.line.y1(), self.line.y2())
        rect = QRectF(x1, y1, x2 - x1, y2 - y1)
        return rect.adjusted(self.corner_radius / 2, self.corner_radius / 2,
                             self.corner_radius / 2, self.corner_radius / 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(self.line.p1())
        path.lineTo(self.line.p2())
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.border_color)
        painter.setBrush(self.color)
        if self.is_hover:
            painter.setPen(Qt.GlobalColor.blue)
        if self.is_selected:
            painter.setPen(Qt.GlobalColor.blue)
        painter.drawLine(self.line)
        painter.drawEllipse(self.line.p1(), self.corner_radius, self.corner_radius)
        painter.drawEllipse(self.line.p2(), self.corner_radius, self.corner_radius)
