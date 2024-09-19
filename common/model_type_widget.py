import enum

from PySide6.QtCore import Qt, QPoint, Signal, Slot, QLine
from PySide6.QtGui import QPaintEvent, QPainter, QPolygon, QPen, QCursor, QImage
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import themeColor, BodyLabel, SimpleCardWidget

from common.custom_icon import CustomFluentIcon
from common.utils import CustomColor


class ModelType(enum.Enum):
    CLASSIFY = 0
    DETECTION = 1
    SEGMENT = 2
    OBB = 3
    POSE = 4

    @property
    def color(self):
        _color_map = {
            ModelType.CLASSIFY: CustomColor.BLUE.value,
            ModelType.DETECTION: CustomColor.BROWN.value,
            ModelType.SEGMENT: CustomColor.YELLOW.value,
            ModelType.OBB: CustomColor.GRAY.value,
            ModelType.POSE: CustomColor.PURPLE.value
        }
        return _color_map[self]

    @property
    def icon(self):
        _icon_map = {
            ModelType.CLASSIFY: CustomFluentIcon.CLASSIFY.colored(*self.color),
            ModelType.DETECTION: CustomFluentIcon.DETECT.colored(*self.color),
            ModelType.SEGMENT: CustomFluentIcon.SEGMENT.colored(*self.color),
            ModelType.OBB: CustomFluentIcon.OBB.colored(*self.color),
            ModelType.POSE: CustomFluentIcon.POSE.colored(*self.color),
        }
        return _icon_map[self]


class ModelTypeItemWidget(SimpleCardWidget):
    item_selected = Signal()

    def __init__(self, name: str, pic_url: str, model_type: ModelType):
        super().__init__()
        self.setFixedSize(120, 120)
        self.vly_content = QVBoxLayout(self)
        self.title = BodyLabel(name, self)
        self.title.setFixedWidth(120)
        self.vly_content.setContentsMargins(0, 0, 0, 0)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.selected = False
        self.pic_url = pic_url
        self.model_type = model_type

    def mousePressEvent(self, event):
        # 当鼠标点击时，记录点击位置
        self.selected = True
        self.item_selected.emit()
        self.update()  # 请求重绘

    def draw_selected(self, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 绘制自定义边框
        painter.setPen(QPen(themeColor(), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        # 绘制右下角的三角形
        triangle = QPolygon([
            QPoint(self.width(), self.height()),
            QPoint(self.width() - int(self.width() / 4), self.height()),
            QPoint(self.width(), self.height() - int(self.height() / 4))
        ])
        triangle_pen = QPen(themeColor(), 1)
        painter.setPen(triangle_pen)
        painter.setBrush(themeColor())
        painter.drawPolygon(triangle)

        # 绘制对勾
        start = QPoint(self.width() - int(self.width() * 0.13), self.height() - int(self.height() * 0.08))
        mid = QPoint(self.width() - int(self.width() * 0.09), self.height() - int(self.height() * 0.05))
        end = QPoint(self.width() - int(self.width() * 0.05), self.height() - int(self.height() * 0.15))
        lines = [QLine(start, mid), QLine(mid, end)]
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLines(lines)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.drawImage(0, 30, QImage(self.pic_url))
        painter.end()

        if self.selected:
            painter.begin(self)
            self.draw_selected(painter)
            painter.end()

    def disable_selected(self):
        self.selected = False
        self.update()

    def enable_selected(self):
        self.selected = True
        self.update()


class ModelTypeGroupWidget(QWidget):
    model_type_selected = Signal(ModelType)

    def __init__(self):
        super().__init__()
        self.hly_content = QHBoxLayout(self)
        self.hly_content.setContentsMargins(0, 0, 0, 0)
        self._init_type_item()

    def _init_type_item(self):
        type_classify = ModelTypeItemWidget(self.tr("classify"), "resource/images/classify.png", ModelType.CLASSIFY)
        type_classify.enable_selected()
        type_detect = ModelTypeItemWidget(self.tr("detect"), "resource/images/detect.png", ModelType.DETECTION)
        type_segment = ModelTypeItemWidget(self.tr("segment"), "resource/images/segment.png", ModelType.SEGMENT)
        type_obb = ModelTypeItemWidget(self.tr("obb"), "resource/images/obb.png", ModelType.OBB)
        type_pose = ModelTypeItemWidget(self.tr("pose"), "resource/images/pose.png", ModelType.POSE)
        self.addItem(type_classify)
        self.addItem(type_detect)
        self.addItem(type_segment)
        self.addItem(type_obb)
        self.addItem(type_pose)

    def addItem(self, item: ModelTypeItemWidget):
        self.hly_content.addWidget(item)
        item.item_selected.connect(self._on_item_selected)

    def _disable_all_items_selected(self):
        for i in range(self.hly_content.count()):
            item = self.hly_content.itemAt(i)
            type_item_widget = item.widget()
            if isinstance(type_item_widget, ModelTypeItemWidget):
                type_item_widget.disable_selected()

    @Slot()
    def _on_item_selected(self):
        self._disable_all_items_selected()
        sender = self.sender()
        if isinstance(sender, ModelTypeItemWidget):
            sender.enable_selected()
            self.model_type_selected.emit(sender.model_type)
