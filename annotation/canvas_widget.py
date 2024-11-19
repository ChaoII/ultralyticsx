import math
from pathlib import Path

from PySide6.QtCore import QLineF, Signal, QPointF
from PySide6.QtCore import QUuid
from PySide6.QtGui import QPolygonF, Qt, QPen, QPainter, QColor, QPixmap, QTransform, QWheelEvent, QKeyEvent, \
    QResizeEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from qfluentwidgets import isDarkTheme, SmoothScrollDelegate

from annotation.shape import RectangleItem, ShapeType, LineItem, CircleItem, PointItem, PolygonItem, ShapeItem, \
    ImageItem, RotatedRectangleItem
from common.component.model_type_widget import ModelType
from .core import drawing_status_manager, DrawingStatus

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
    shape_item_selected_changed = Signal(str)
    delete_shape_item_clicked = Signal(str)
    width_changed = Signal(int)

    def __init__(self):
        super().__init__()

        # 创建绘图场景
        self.scene = QGraphicsScene(self)
        self.scene.selectionChanged.connect(self.on_item_select_changed)
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
        self.current_shape_type = ShapeType.RotatedRectangle
        # 绘制状态
        self.background_pix = QPixmap()
        self.is_drawing = False
        self.start_pos = None
        self.end_pos = None
        self.scale_factor = 1
        self.ensure_point_num = 0
        self.rotated_rect_points = QPolygonF()
        self.polygon_points = QPolygonF()
        self.polygon_first_point_hover = False
        # 临时图形
        self.temp_item: ShapeItem | None = None
        self.shape_item_map = dict()

    def on_item_select_changed(self):
        for item in self.scene.selectedItems():
            if isinstance(item, ShapeItem):
                self.shape_item_selected_changed.emit(item.get_id())

    def get_shape_item(self, uid: str):
        return self.shape_item_map.get(uid, None)

    def get_shape_items(self):
        return self.scene.items()

    def get_background_pix(self):
        return self.background_pix

    def delete_shape_item(self, uid):
        shape_item = self.shape_item_map.get(uid, None)
        if shape_item:
            self.scene.removeItem(shape_item)
            self.shape_item_map.pop(uid)

    def update_shape_item_color(self, annotation, color: QColor):
        for uid, shape_item in self.shape_item_map.items():
            if shape_item.get_annotation() == annotation:
                if isinstance(shape_item, ShapeItem):
                    shape_item.set_color(color)

    def set_shape_item_selected(self, uid):
        self.scene.clearSelection()
        shape_item = self.shape_item_map.get(uid, None)
        if shape_item:
            shape_item.setSelected(True)

    def send_draw_finished_signal(self, shape_item: ShapeItem):
        uid = QUuid.createUuid().toString().replace("-", "").replace("{", "").replace("}", "")
        shape_item.set_id(uid)
        shape_item.prepareGeometryChange()
        self.shape_item_map.update({uid: shape_item})
        self.draw_finished.emit(shape_item)

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

    def set_image_and_draw_annotations(self, image_path: str | Path, annotations: list[list[float]],
                                       model_type: ModelType, labels_color: dict):
        self.background_pix = QPixmap(image_path)
        image_item = ImageItem(self.background_pix)
        self.scene.clear()
        self.setSceneRect(self.background_pix.rect())
        self.scene.addItem(image_item)
        for annotation in annotations:
            label_index = int(annotation[0])
            shape_data = annotation[1:]
            label = list(labels_color.keys())[label_index]
            color = labels_color[label]
            if model_type == ModelType.DETECT:
                shape_item = RectangleItem()
                x_center = float(shape_data[0]) * self.background_pix.width()
                y_center = float(shape_data[1]) * self.background_pix.height()
                w = float(shape_data[2]) * self.background_pix.width()
                h = float(shape_data[3]) * self.background_pix.height()
                p1 = QPointF(x_center - w / 2, y_center - h / 2)
                p2 = QPointF(x_center + w / 2, y_center + h / 2)
                shape_item.update_points([p1, p2])
            elif model_type == ModelType.OBB:
                shape_item = RotatedRectangleItem()
                x1 = float(shape_data[0]) * self.background_pix.width()
                y1 = float(shape_data[1]) * self.background_pix.height()
                x2 = float(shape_data[2]) * self.background_pix.width()
                y2 = float(shape_data[3]) * self.background_pix.height()
                x3 = float(shape_data[4]) * self.background_pix.width()
                y3 = float(shape_data[5]) * self.background_pix.height()
                x4 = float(shape_data[6]) * self.background_pix.width()
                y4 = float(shape_data[7]) * self.background_pix.height()
                p1 = QPointF(x1, y1)
                p2 = QPointF(x2, y2)
                p3 = QPointF((x3 + x4) / 2, (y3 + y4) / 2)
                shape_item.update_points([p1, p2, p3])
            elif model_type == ModelType.SEGMENT:
                shape_item = PolygonItem()
                points = []
                for i in range(0, len(shape_data), 2):
                    x = float(shape_data[i]) * self.background_pix.width()
                    y = float(shape_data[i + 1]) * self.background_pix.height()
                    points.append(QPointF(x, y))
                shape_item.update_points(points)
            elif model_type == ModelType.POSE:
                shape_item = LineItem()
                x1 = float(shape_data[0]) * self.background_pix.width()
                y1 = float(shape_data[1]) * self.background_pix.height()
                x2 = float(shape_data[2]) * self.background_pix.width()
                y2 = float(shape_data[3]) * self.background_pix.height()
                shape_item.update_points([QPointF(x1, y1), QPointF(x2, y2)])
            else:
                raise NotImplementedError
            shape_item.set_annotation(label)
            shape_item.set_color(color)
            shape_item.set_is_drawing_history(True)
            self.scene.addItem(shape_item)
            self.send_draw_finished_signal(shape_item)

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

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.width_changed.emit(event.size().width())
        super().resizeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if drawing_status_manager.get_drawing_status() == DrawingStatus.Select:
            if event.key() == Qt.Key.Key_Shift:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

            if event.key() == Qt.Key.Key_Delete:
                for item in self.scene.selectedItems():
                    if isinstance(item, ShapeItem):
                        self.delete_shape_item_clicked.emit(item.get_id())
                        self.scene.removeItem(item)
                        if item.get_id() in self.shape_item_map:
                            self.shape_item_map.pop(item.get_id())

            if event.key() == Qt.Key.Key_Up:
                for item in self.scene.selectedItems():
                    if isinstance(item, ShapeItem):
                        item.move_by(QPointF(0, -1))
            elif event.key() == Qt.Key.Key_Down:
                for item in self.scene.selectedItems():
                    if isinstance(item, ShapeItem):
                        item.move_by(QPointF(0, 1))
            elif event.key() == Qt.Key.Key_Left:
                for item in self.scene.selectedItems():
                    if isinstance(item, ShapeItem):
                        item.move_by(QPointF(-1, 0))
            elif event.key() == Qt.Key.Key_Right:
                for item in self.scene.selectedItems():
                    if isinstance(item, ShapeItem):
                        item.move_by(QPointF(1, 0))
            else:
                super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if drawing_status_manager.get_drawing_status() == DrawingStatus.Select:
            if event.key() == Qt.Key.Key_Shift:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
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
                elif self.current_shape_type == ShapeType.RotatedRectangle:
                    if not self.is_drawing:
                        self.temp_item = RotatedRectangleItem()
                        self.scene.addItem(self.temp_item)
                        self.rotated_rect_points = QPolygonF()
                        self.rotated_rect_points.append(self.start_pos)
                elif self.current_shape_type == ShapeType.Point:
                    self.temp_item = PointItem()
                    self.scene.addItem(self.temp_item)
                elif self.current_shape_type == ShapeType.Line:
                    self.temp_item = LineItem()
                    self.scene.addItem(self.temp_item)
                self.set_is_drawing(True)
                self.update_temp_item()
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
            # 鼠标按下后再释放，记录完成了一个点
            self.ensure_point_num += 1
            # 两点即可绘制出矩形，圆形，直线
            if self.current_shape_type == ShapeType.Line or self.current_shape_type == ShapeType.Rectangle or \
                    self.current_shape_type == ShapeType.Circle:
                if self.ensure_point_num == 2:
                    self.ensure_point_num = 0
                    self.set_is_drawing(False)
                    self.send_draw_finished_signal(self.temp_item)
                else:
                    self.set_is_drawing(True)
            # 一点即可绘制一个点
            elif self.current_shape_type == ShapeType.Point:
                if self.ensure_point_num == 1:
                    self.ensure_point_num = 0
                    self.set_is_drawing(False)
                    self.send_draw_finished_signal(self.temp_item)
                else:
                    self.set_is_drawing(True)
            # 多点绘制多边形，绘制完成则闭合，通过闭合条件判断绘制完成
            elif self.current_shape_type == ShapeType.Polygon:
                if self.polygon_first_point_hover:
                    self.ensure_point_num = 0
                    # 丢弃最后一个点直接闭合曲线
                    self.polygon_points.pop_back()
                    self.temp_item.update_points(self.polygon_points.toList())
                    self.set_is_drawing(False)
                    if isinstance(self.temp_item, PolygonItem):
                        self.temp_item.set_first_point_hover(False)
                    self.polygon_first_point_hover = False
                    self.send_draw_finished_signal(self.temp_item)
                else:
                    self.polygon_points.append(self.end_pos)
                    self.set_is_drawing(True)
            # 三点绘制旋转矩形
            elif self.current_shape_type == ShapeType.RotatedRectangle:
                if self.ensure_point_num == 3:
                    self.ensure_point_num = 0
                    self.set_is_drawing(False)
                    self.send_draw_finished_signal(self.temp_item)
                else:
                    self.rotated_rect_points.append(self.end_pos)
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
        elif self.current_shape_type == ShapeType.RotatedRectangle:
            points = self.rotated_rect_points.toList()
            if len(points) >= 2:
                points[-1] = self.end_pos
                self.rotated_rect_points = QPolygonF(points)
            self.temp_item.update_points(points)
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
