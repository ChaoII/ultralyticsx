import enum

from PySide6.QtCore import QPointF, QRectF, Qt, QLineF
from PySide6.QtGui import QPolygonF, QPainterPath, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent


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
        self.path = QPainterPath()

    def set_path(self, path: QPolygonF):
        self.path.addPolygon(path)

    def shape(self) -> QPainterPath:
        return self.path

    def boundingRect(self) -> QRectF:
        if self.path.isEmpty():
            return QRectF()
        return self.path.controlPointRect()

    def paint(self, painter, option, widget=None):
        painter.drawPath(self.path)


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
        self.update()

    def boundingRect(self) -> QRectF:
        return self.rect.adjusted(self.corner_radius / 2, self.corner_radius / 2, self.corner_radius / 2,
                                  self.corner_radius / 2)

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
        self.update()

    def boundingRect(self) -> QRectF:

        return QRectF(self.line.p1(), self.line.p2()).adjusted(self.corner_radius / 2, self.corner_radius / 2,
                                                               self.corner_radius / 2,
                                                               self.corner_radius / 2)

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
