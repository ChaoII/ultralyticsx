import math
from pathlib import Path

from PySide6.QtCore import QRectF, QPointF, QLineF
from PySide6.QtGui import QPolygonF, Qt, QPen, QPainter, QColor, QPixmap, QTransform, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem
from qfluentwidgets import isDarkTheme

from annotation.shape import RectangleItem, ShapeType, LineItem

# dark_theme/light theme
VIEW_BACKGROUND_COLOR = [QColor(53, 53, 53), QColor(53, 53, 53)]
VIEW_INTER_LINE_COLOR = [QColor(60, 60, 60), QColor(60, 60, 60)]
VIEW_BORDER_LINE_COLOR = [QColor(0, 0, 0), QColor(0, 0, 0)]

VIEW_INTER_LINE_STEP = 15
VIEW_BORDER_LINE_STEP = 150

SCALE_RANGE = [0.3, 4.0]
SCALE_STEP = 1.1


class InteractiveCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        # 创建绘图场景
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.setScene(self.scene)
        # 必须加不加的话刷新不及时，有残影
        self.setMouseTracking(True)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # 当前形状类型
        self.current_shape_type = ShapeType.Rectangle
        self.inter_line_color = QColor(Qt.GlobalColor.red)
        self.border_line_color = QColor(Qt.GlobalColor.cyan)
        self.update_background_color()
        # 鼠标状态
        self.is_drawing = False
        self.start_pos = None
        self.end_pos = None
        self.scale_factor = 1
        self.line_ensure_point_num = 0

        # 临时图形
        self.temp_item = None

    def update_background_color(self):
        if isDarkTheme():
            self.setBackgroundBrush(VIEW_BACKGROUND_COLOR[0])
            self.inter_line_color = VIEW_INTER_LINE_COLOR[0]
            self.border_line_color = VIEW_BORDER_LINE_COLOR[0]
        else:
            self.setBackgroundBrush(VIEW_BACKGROUND_COLOR[1])
            self.inter_line_color = VIEW_INTER_LINE_COLOR[1]
            self.border_line_color = VIEW_BORDER_LINE_COLOR[1]

    def set_image(self, image_path: str | Path):
        pix = QPixmap(image_path)
        image_item = QGraphicsPixmapItem(pix)
        self.setSceneRect(pix.rect())
        self.scene.addItem(image_item)

    def set_shape_type(self, shape_type: ShapeType):
        self.current_shape_type = shape_type

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() >= 0:
                self.scale_up()
            else:
                self.scale_down()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = True
            self.start_pos = self.mapToScene(event.pos())
            self.end_pos = self.start_pos
            if self.current_shape_type == ShapeType.Rectangle:
                self.temp_item = RectangleItem()
                self.scene.addItem(self.temp_item)
            elif self.current_shape_type == ShapeType.Circle:
                self.temp_item = self.scene.addEllipse(QRectF(), QPen(Qt.GlobalColor.red))
            elif self.current_shape_type == ShapeType.Polygon:
                self.temp_item = self.scene.addPolygon(QRectF(), QPen(Qt.GlobalColor.red))
            elif self.current_shape_type == ShapeType.Line:
                # self.temp_item = LineItem()
                # self.scene.addItem(self.temp_item)
                self.temp_item = self.scene.addLine(QLineF())
            self.update_temp_item()
        self.update()

    def mouseMoveEvent(self, event):
        # if self.is_drawing and event.buttons() & Qt.MouseButton.LeftButton:
        if self.is_drawing:
            self.end_pos = self.mapToScene(event.pos())
            self.update_temp_item()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_pos = self.mapToScene(event.pos())
            self.update_temp_item()
            if self.current_shape_type == ShapeType.Rectangle or self.current_shape_type == ShapeType.Circle or self.current_shape_type == ShapeType.Point:
                self.is_drawing = False
                self.temp_item = None
            if self.current_shape_type == ShapeType.Line:
                self.line_ensure_point_num += 1
                if self.line_ensure_point_num == 2:
                    self.line_ensure_point_num = 0
                    self.is_drawing = False
                    self.temp_item = None
        self.update()

    def update_temp_item(self):
        if self.current_shape_type == ShapeType.Rectangle:
            rect = QRectF(self.start_pos, self.end_pos)
            self.temp_item.set_rect(rect)
        elif self.current_shape_type == ShapeType.Circle:
            rect = QRectF(self.start_pos, self.end_pos)
            self.temp_item.setRect(rect)
        elif self.current_shape_type == ShapeType.Polygon:
            points = [QPointF(self.start_pos), QPointF(self.end_pos)]
            polygon = QPolygonF(points)
            self.temp_item.setPolygon(polygon)
        elif self.current_shape_type == ShapeType.Line:
            line = QLineF(self.start_pos, self.end_pos)
            self.temp_item.setLine(line)

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
