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
        self.color = themeColor()
        self.is_hover = False
        self.is_selected = False
        self.corner_radius = 4
        self.hover_index = -1
        self.points: list[QPointF] = []
        # 记录鼠标点击时所在的点
        self.press_point = QPointF()

    @staticmethod
    def get_shape_type() -> ShapeType:
        raise NotImplementedError

    def update_points(self, points: list[QPointF]):
        self.points = points
        self.update_shape()

    def update_shape(self):
        raise NotImplementedError

    def get_shape_data(self) -> list:
        raise NotImplementedError

    def set_hover(self, is_hover: bool):
        self.is_hover = is_hover

    def set_selected(self, is_selected: bool):
        self.is_selected = is_selected

    def move_by(self, offset: QPointF):
        raise NotImplementedError

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


class PolygonLineItem(ShapeItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.polygon_points = QPolygonF()
        self.close_status = False
        self.first_point_hover = False
        self.corner_radius = 8

    def update_shape_data(self, polygon: QPolygonF):
        self.polygon_points = polygon

    def get_shape_type(self) -> ShapeType:
        return ShapeType.Polygon

    def get_shape_data(self):
        return self.polygon_points.toList()

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
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


class RectangleItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.rect = QRectF()
        # 记录鼠标按下时的矩形快照
        self.press_rect = QRectF()
        self.operation_type = RectangleItem.OperationType.Move

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Rectangle

    def move_by(self, offset: QPointF):
        self.rect.translate(offset)
        self.points[0] = self.rect.topLeft()
        self.points[1] = self.rect.bottomRight()
        self.update()

    def set_color(self, color: QColor):
        self.color = color

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
        return self.rect.adjusted(-self.corner_radius / 2, -self.corner_radius / 2,
                                  self.corner_radius / 2, self.corner_radius / 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.rect.adjusted(-self.corner_radius / 2, -self.corner_radius / 2,
                                        self.corner_radius / 2, self.corner_radius / 2))
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        brush_color = QColor(self.color)
        if self.is_hover:
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
        if self.is_selected:
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        painter.drawRect(self.rect)

        painter.setBrush(self.color)

        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, self.corner_radius, self.corner_radius)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.operation_type == RectangleItem.OperationType.Move:
            delta = event.pos() - self.press_point
            self.rect = self.press_rect.translated(delta)
            self.points[0] = self.rect.topLeft()
            self.points[1] = self.rect.bottomRight()
        else:
            self.points[self.hover_index] = event.pos()
            self.update_shape()
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton \
                and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if self.operation_type == RectangleItem.OperationType.Move:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.press_point = event.pos()
                self.press_rect = QRectF(self.rect)
            self.is_selected = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

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

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = True
            self.update()

    def hoverLeaveEvent(self, event):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = False
            self.update()


class CircleItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.operation_type = RectangleItem.OperationType.Move
        # 记录鼠标按下时的矩形快照
        self.press_circle = [QPointF(0, 0), QPointF(0, 0)]

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Circle

    def move_by(self, offset: QPointF):
        self.points[0] = self.points[0] + offset
        self.points[1] = self.points[1] + offset
        self.update()

    def set_color(self, color: QColor):
        self.color = color

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
        return rect.adjusted(-self.corner_radius / 2, -self.corner_radius / 2,
                             self.corner_radius / 2, self.corner_radius / 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        radius = self.calculate_radius()
        path.addEllipse(self.points[0], radius, radius)
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        brush_color = QColor(self.color)
        if self.is_hover:
            brush_color.setAlpha(100)
            painter.setBrush(brush_color)
        if self.is_selected:
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        radius = self.calculate_radius()
        painter.drawEllipse(self.points[0], radius, radius)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, self.corner_radius, self.corner_radius)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.operation_type == RectangleItem.OperationType.Move:
            delta = event.pos() - self.press_point
            self.points = [self.press_circle[0] + delta, self.press_circle[1] + delta]
        else:
            self.points[self.hover_index] = event.pos()
            self.update_shape()
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton \
                and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if self.operation_type == RectangleItem.OperationType.Move:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.press_point = event.pos()
                self.press_circle = self.points
            self.is_selected = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

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

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = True
            self.update()

    def hoverLeaveEvent(self, event):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = False
            self.update()


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

    def move_by(self, offset: QPointF):
        self.points[0] = self.points[0] + offset
        self.update()

    def set_color(self, color: QColor):
        self.color = color

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

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton \
                and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_selected = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.is_selected = False
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.update()

    def hoverLeaveEvent(self, event):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = False
            self.update()


class LineItem(ShapeItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.operation_type = RectangleItem.OperationType.Move
        self.line = QLineF()
        # 记录鼠标按下时的直线快照
        self.press_line = QLineF()

    @staticmethod
    def get_shape_type() -> ShapeType:
        return ShapeType.Line

    def move_by(self, offset: QPointF):
        self.points[0] = self.points[0] + offset
        self.points[1] = self.points[1] + offset
        self.update_shape()
        self.update()

    def set_color(self, color: QColor):
        self.color = color

    def update_shape(self):
        self.line = QLineF(self.points[0], self.points[1])
        angle = self.line.angle()
        length = self.line.length()
        margin = 5  # 容差范围

        # 创建旋转矩形
        rect = QRectF(0, -margin, length, 2 * margin)
        transform = QTransform()
        transform.translate(self.points[0].x(), self.points[0].y())
        transform.rotate(angle)
        self.rotated_rect = transform.mapRect(rect)
        self.path = QPainterPath()
        self.path.addRect(self.rotated_rect)

    def get_shape_data(self):
        return [self.line.x1(), self.line.y1(), self.line.x2(), self.line.y2()]

    def boundingRect(self) -> QRectF:
        x1 = min(self.points[0].x(), self.points[1].x())
        y1 = min(self.points[0].y(), self.points[1].y())
        x2 = max(self.points[0].x(), self.points[1].x())
        y2 = max(self.points[0].y(), self.points[1].y())
        rect = QRectF(QPointF(x1, y1), QPointF(x2, y2))
        return rect.adjusted(self.corner_radius / 2, self.corner_radius / 2,
                             self.corner_radius / 2, self.corner_radius / 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(self.line.p1())
        path.lineTo(self.line.p2())

        angle = self.line.angle()
        length = self.line.length()
        margin = 5  # 容差范围

        # 创建旋转矩形
        rect = QRectF(0, -margin, length, 2 * margin)
        transform = QTransform()
        transform.translate(self.points[0].x(), self.points[0].y())
        transform.rotate(angle)
        self.rotated_rect = transform.mapRect(rect)
        path.addRect(self.rotated_rect)
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.is_hover:
            painter.setPen(QPen(self.color, 2, Qt.PenStyle.SolidLine))
        if self.is_selected:
            painter.setPen(QPen(self.color, 1, Qt.PenStyle.DashLine))
        painter.drawLine(self.line)
        painter.setBrush(self.color)
        for index, point in enumerate(self.points):
            if index == self.hover_index:
                painter.drawEllipse(point, self.corner_radius * 2, self.corner_radius * 2)
            else:
                painter.drawEllipse(point, self.corner_radius, self.corner_radius)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.operation_type == RectangleItem.OperationType.Move:
            delta = event.pos() - self.press_point
            self.points = [self.press_line.p1() + delta, self.press_line.p2() + delta]
        else:
            self.points[self.hover_index] = event.pos()
        self.update_shape()
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton \
                and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            if self.operation_type == RectangleItem.OperationType.Move:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.press_point = event.pos()
                self.press_line = QLineF(self.line)
            self.is_selected = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

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

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = True
            self.update()

    def hoverLeaveEvent(self, event):
        if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
            self.is_hover = False
            self.update()

# class LineItem(ShapeItem):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
#         self.setAcceptHoverEvents(True)
#         self.line = QLineF()
#         self.color = Qt.GlobalColor.red
#         self.border_color = Qt.GlobalColor.black
#         self.border_width = 2
#         self.is_hover = False
#         self.is_selected = False
#         self.is_dragging = False
#         self.is_moving = False
#         self.corner_radius = 8
#
#     def get_shape_type(self) -> ShapeType:
#         return ShapeType.Line
#
#     def update_shape_data(self, line: QLineF):
#         self.line = line
#
#     def get_shape_data(self):
#         # x_center, y_center, w, h
#         return [self.line.x1(), self.line.y1(), self.line.x2(), self.line.y2()]
#
#     def boundingRect(self) -> QRectF:
#
#         x1 = min(self.line.x1(), self.line.x2())
#         y1 = min(self.line.y1(), self.line.y2())
#         x2 = max(self.line.x1(), self.line.x2())
#         y2 = max(self.line.y1(), self.line.y2())
#         rect = QRectF(x1, y1, x2 - x1, y2 - y1)
#         return rect.adjusted(self.corner_radius / 2, self.corner_radius / 2,
#                              self.corner_radius / 2, self.corner_radius / 2)
#
#     def shape(self) -> QPainterPath:
#         path = QPainterPath()
#         path.moveTo(self.line.p1())
#         path.lineTo(self.line.p2())
#         return path
#
#     def paint(self, painter, option, widget=None):
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.setPen(self.border_color)
#         painter.setBrush(self.color)
#         if self.is_hover:
#             painter.setPen(Qt.GlobalColor.blue)
#         if self.is_selected:
#             painter.setPen(Qt.GlobalColor.blue)
#         painter.drawLine(self.line)
#         painter.drawEllipse(self.line.p1(), self.corner_radius, self.corner_radius)
#         painter.drawEllipse(self.line.p2(), self.corner_radius, self.corner_radius)
