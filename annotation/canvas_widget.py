import enum
import math
from pathlib import Path

from PySide6.QtCore import QRectF, QLineF, Signal, QPointF
from PySide6.QtGui import QPolygonF, Qt, QPen, QPainter, QColor, QPixmap, QTransform, QWheelEvent, QKeyEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from qfluentwidgets import isDarkTheme, SmoothScrollDelegate
from .core import drawing_status_manager, DrawingStatus
from annotation.shape import RectangleItem, ShapeType, LineItem, CircleItem, PointItem, PolygonItem, ShapeItem

# dark_theme/light theme
VIEW_BACKGROUND_COLOR = [QColor(53, 53, 53), QColor(53, 53, 53)]
VIEW_INTER_LINE_COLOR = [QColor(60, 60, 60), QColor(60, 60, 60)]
VIEW_BORDER_LINE_COLOR = [QColor(0, 0, 0), QColor(0, 0, 0)]

VIEW_INTER_LINE_STEP = 15
VIEW_BORDER_LINE_STEP = 150

SCALE_RANGE = [0.3, 4.0]
SCALE_STEP = 1.1


class InteractiveCanvas(QGraphicsView):
    is_drawing_changed = Signal(bool)
    draw_finished = Signal(ShapeItem)

    def __init__(self):
        super().__init__()

        # 创建绘图场景
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setMouseTracking(True)
        # 必须加不加的话刷新不及时，有残影
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scrollDelegate = SmoothScrollDelegate(self)

        self.inter_line_color = QColor(Qt.GlobalColor.red)
        self.border_line_color = QColor(Qt.GlobalColor.cyan)
        self.update_background_color()
        # 当前形状类型
        self.current_shape_type = ShapeType.Rectangle
        # 绘制状态
        self.is_drawing = False
        self.start_pos = None
        self.end_pos = None
        self.scale_factor = 1
        self.ensure_point_num = 0
        self.polygon_points = QPolygonF()
        self.polygon_first_point_hover = False
        # 临时图形
        self.temp_item: ShapeItem | None = None

    def update_background_color(self):
        if isDarkTheme():
            self.setBackgroundBrush(VIEW_BACKGROUND_COLOR[0])
            self.inter_line_color = VIEW_INTER_LINE_COLOR[0]
            self.border_line_color = VIEW_BORDER_LINE_COLOR[0]
        else:
            self.setBackgroundBrush(VIEW_BACKGROUND_COLOR[1])
            self.inter_line_color = VIEW_INTER_LINE_COLOR[1]
            self.border_line_color = VIEW_BORDER_LINE_COLOR[1]

    def clear(self):
        self.scene.clear()
        self.scene.setSceneRect(0, 0, 800, 600)

    def set_image(self, image_path: str | Path):
        pix = QPixmap(image_path)
        image_item = QGraphicsPixmapItem(pix)
        self.scene.clear()
        self.setSceneRect(pix.rect())
        self.scene.addItem(image_item)

    def set_drawing_status(self, status: DrawingStatus):
        drawing_status_manager.set_drawing_status(status)
        if status != DrawingStatus.Draw:
            self.is_drawing = False

    def set_shape_type(self, shape_type: ShapeType):
        self.current_shape_type = shape_type

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() >= 0:
                self.scale_up()
            else:
                self.scale_down()

    def set_is_drawing(self, is_drawing: bool):
        self.is_drawing = is_drawing
        self.is_drawing_changed.emit(self.is_drawing)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if drawing_status_manager.get_drawing_status() != DrawingStatus.Draw:
                for item in self.scene.items():
                    if isinstance(item, ShapeItem):
                        item.set_selected(False)

            if drawing_status_manager.get_drawing_status() == DrawingStatus.Draw and not self.is_drawing:
                self.start_pos = self.mapToScene(event.pos())
                self.end_pos = self.start_pos
                if self.current_shape_type == ShapeType.Rectangle:
                    self.temp_item = RectangleItem()
                    self.scene.addItem(self.temp_item)
                elif self.current_shape_type == ShapeType.Circle:
                    self.temp_item = CircleItem()
                    self.scene.addItem(self.temp_item)
                elif self.current_shape_type == ShapeType.Polygon:
                    if not self.polygon_first_point_hover and not self.is_drawing:
                        self.temp_item = PolygonItem()
                        self.scene.addItem(self.temp_item)
                        self.polygon_points = QPolygonF()
                        self.polygon_points.append(self.start_pos)
                elif self.current_shape_type == ShapeType.Point:
                    self.temp_item = PointItem()
                    self.scene.addItem(self.temp_item)
                elif self.current_shape_type == ShapeType.Line:
                    self.temp_item = LineItem()
                    self.scene.addItem(self.temp_item)
                self.set_is_drawing(True)
                self.update_temp_item()
            # else:
            #     self.is_drawing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_pos = self.mapToScene(event.pos())
            self.update_temp_item()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_pos = self.mapToScene(event.pos())
            self.update_temp_item()
            self.ensure_point_num += 1
            if self.current_shape_type == ShapeType.Line or self.current_shape_type == ShapeType.Rectangle or \
                    self.current_shape_type == ShapeType.Circle:
                # 两点即可绘制出图形
                if self.ensure_point_num == 2:
                    self.ensure_point_num = 0
                    self.set_is_drawing(False)
                    self.draw_finished.emit(self.temp_item)
                else:
                    self.set_is_drawing(True)
            elif self.current_shape_type == ShapeType.Point:
                if self.ensure_point_num == 1:
                    self.ensure_point_num = 0
                    self.set_is_drawing(False)
                    self.draw_finished.emit(self.temp_item)
                else:
                    self.set_is_drawing(True)
            elif self.current_shape_type == ShapeType.Polygon:
                if self.polygon_first_point_hover:
                    self.ensure_point_num = 0
                    # 丢弃最后一个点直接闭合曲线
                    self.polygon_points.pop_back()
                    # self.polygon_points.append(self.polygon_points.value(0))
                    self.temp_item.update_points(self.polygon_points.toList())
                    self.set_is_drawing(False)
                    if isinstance(self.temp_item, PolygonItem):
                        self.temp_item.set_first_point_hover(False)
                    self.polygon_first_point_hover = False
                    self.draw_finished.emit(self.temp_item)
                else:
                    self.polygon_points.append(self.end_pos)
                    self.set_is_drawing(True)
        super().mouseReleaseEvent(event)

    def update_temp_item(self):
        if self.current_shape_type == ShapeType.Rectangle:
            self.temp_item.update_points([self.start_pos, self.end_pos])
        elif self.current_shape_type == ShapeType.Circle:
            self.temp_item.update_points([self.start_pos, self.end_pos])
        elif self.current_shape_type == ShapeType.Polygon:
            points = self.polygon_points.toList()
            if points and len(points) >= 2:
                points[-1] = self.end_pos
                self.polygon_points = QPolygonF(points)
                d_point = self.polygon_points.value(0) - self.polygon_points.value(self.polygon_points.size() - 1)
                distance = math.sqrt(d_point.x() ** 2 + d_point.y() ** 2)
                if distance < 8:
                    self.polygon_first_point_hover = True
                    if isinstance(self.temp_item, PolygonItem):
                        self.temp_item.set_first_point_hover(True)
                else:
                    self.polygon_first_point_hover = False
                    if isinstance(self.temp_item, PolygonItem):
                        self.temp_item.set_first_point_hover(False)
            self.temp_item.update_points(self.polygon_points.toList())
            # self.polygon_points.pop_back()
        elif self.current_shape_type == ShapeType.Point:
            self.temp_item.update_points([self.end_pos])
        elif self.current_shape_type == ShapeType.Line:
            self.temp_item.update_points([self.start_pos, self.end_pos])
        self.temp_item.update()

    def drawBackground(self, painter: QPainter, rect) -> None:
        super().drawBackground(painter, rect)

        def draw_grid(grid_step):
            lt = self.mapToScene(self.rect().topLeft())
            rb = self.mapToScene(self.rect().bottomRight())

            left = math.floor(lt.x() / grid_step - 0.5)
            right = math.ceil(rb.x() / grid_step + 1.0)
            bottom = math.floor(lt.y() / grid_step - 0.5)
            top = math.floor(rb.y() / grid_step + 1.0)

            for i in range(left, right):
                line = QLineF(i * grid_step, bottom * grid_step, i * grid_step, top * grid_step)
                painter.drawLine(line)

            for i in range(bottom, top):
                line = QLineF(left * grid_step, i * grid_step, right * grid_step, i * grid_step)
                painter.drawLine(line)

        painter.setPen(QPen(self.inter_line_color, 1))
        draw_grid(VIEW_INTER_LINE_STEP)

        painter.setPen(QPen(self.border_line_color, 1))
        draw_grid(VIEW_BORDER_LINE_STEP)

    def setup_scale(self, scale):
        scale = max(SCALE_RANGE[0], min(SCALE_RANGE[1], scale))
        if scale < 0 or scale == self.transform().m11():
            return
        matrix = QTransform()
        matrix.scale(scale, scale)
        self.setTransform(matrix)

    def scale_down(self):
        factor = pow(SCALE_STEP, -1.0)
        if SCALE_RANGE[0] > 0:
            t = self.transform()
            t.scale(factor, factor)
            if t.m11() <= SCALE_RANGE[0]:
                self.setup_scale(t.m11())
                return
        self.scale(factor, factor)
        self.scale_factor *= factor

    def scale_up(self):
        factor = pow(SCALE_STEP, 1.0)
        if SCALE_RANGE[1] > 0:
            t = self.transform()
            t.scale(factor, factor)
            if t.m11() >= SCALE_RANGE[1]:
                self.setup_scale(t.m11())
                return
        self.scale(factor, factor)
        self.scale_factor *= factor

    def reset_scale(self):
        self.scale(1 / self.scale_factor, 1 / self.scale_factor)
        self.scale_factor = 1
