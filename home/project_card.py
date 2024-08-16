from pathlib import Path

from PySide6.QtCore import QRect, QPoint, Signal
from PySide6.QtGui import QMouseEvent, QCursor, Qt, QPainter, QPen, QFont, QColor, QPainterPath
from qfluentwidgets import ElevatedCardWidget, SimpleCardWidget, StrongBodyLabel, TitleLabel, BodyLabel, themeColor, \
    isDarkTheme
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout

from home.new_project import ProjectInfo
from settings import cfg


class ProjectCard(ElevatedCardWidget):
    view_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMouseTracking(True)

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.vly_1 = QVBoxLayout(self)
        self.lbl_project_name = TitleLabel()
        self.lbl_project_id = StrongBodyLabel()
        self.lbl_project_description = BodyLabel()
        self.lbl_project_type = BodyLabel()
        self.lbl_create_time = BodyLabel()
        self.hly_bottom = QHBoxLayout()
        self.hly_bottom.addWidget(self.lbl_project_type)
        self.hly_bottom.addWidget(self.lbl_create_time)
        self.vly_1.addWidget(self.lbl_project_name)
        self.vly_1.addWidget(self.lbl_project_id)
        self.vly_1.addWidget(self.lbl_project_description)
        self.vly_1.addStretch(1)
        self.vly_1.addLayout(self.hly_bottom)
        self.setFixedSize(280, 240)

        self.is_hover_view = False
        self.is_pressed_view = False
        self.is_hover_delete = False
        self.is_pressed_delete = False

        self.view_rect = QRect(0, self.height() - 40, int(self.width() / 2), 40)
        self.delete_rect = QRect(int(self.width() / 2), self.height() - 40, int(self.width() / 2), 40)

    def set_project_info(self, project_info: ProjectInfo):
        self.lbl_project_name.setText(project_info.project_name)
        self.lbl_project_id.setText(project_info.project_id)
        self.lbl_project_description.setText(project_info.project_description)
        self.lbl_project_type.setText(project_info.project_type.name)
        self.lbl_create_time.setText(project_info.create_time)

    def paintEvent(self, e):
        if self.isHover:
            # 绘制自定义边框
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(themeColor(), 2))
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), self.borderRadius, self.borderRadius)
            view_brush_color = themeColor()
            if self.is_hover_view:
                view_brush_color = QColor(themeColor().red(), themeColor().green(), themeColor().blue(), 198)
            if self.is_pressed_view:
                view_brush_color = QColor(themeColor().red(), themeColor().green(), themeColor().blue(), 149)
            painter.setBrush(view_brush_color)

            font = QFont()
            font.setPointSize(11)
            painter.setFont(font)

            # 绘制查看按钮
            path = QPainterPath()
            path.moveTo(self.view_rect.left(), self.view_rect.top())  # 左上角
            path.lineTo(self.view_rect.right(), self.view_rect.top())  # 右上角
            path.lineTo(self.view_rect.right(), self.view_rect.bottom())  # 右上角到右下角
            path.lineTo(self.view_rect.left() + self.borderRadius, self.view_rect.bottom())  # 右下角到圆角前的点
            # 注意这里的坐标和角度，从右下角逆时针绘制到左下角
            path.arcTo(
                QRect(self.view_rect.left(), self.view_rect.bottom() - 2 * self.borderRadius, self.borderRadius * 2,
                      self.borderRadius * 2), 270, -90)
            path.lineTo(self.view_rect.left(), self.view_rect.top())  # 左下角到左上角
            path.closeSubpath()
            painter.drawPath(path)

            delete_brush_color = QColor(0, 0, 0, 0)
            if self.is_hover_delete:
                delete_brush_color = QColor(255, 255, 255, 10) if isDarkTheme() else QColor(0, 0, 0, 10)
            if self.is_pressed_delete:
                delete_brush_color = QColor(255, 255, 255, 20) if isDarkTheme() else QColor(0, 0, 0, 20)

            painter.setBrush(delete_brush_color)
            # 绘制删除按钮
            path = QPainterPath()
            path.moveTo(self.delete_rect.left(), self.delete_rect.top())  # 左上角
            path.lineTo(self.delete_rect.right(), self.delete_rect.top())  # 右上角
            path.lineTo(self.delete_rect.right(), self.delete_rect.bottom() - self.borderRadius)  # 右下角
            path.arcTo(QRect(self.delete_rect.right() - 2 * self.borderRadius,
                             self.delete_rect.bottom() - 2 * self.borderRadius,
                             self.borderRadius * 2, self.borderRadius * 2), 0, -90)
            path.lineTo(self.delete_rect.left(), self.delete_rect.bottom())  # 左下角
            path.lineTo(self.delete_rect.left(), self.delete_rect.top())  # 左下角到左上角
            path.closeSubpath()
            painter.drawPath(path)
            painter.setPen(Qt.GlobalColor.white)

            painter.setPen(QColor(0, 0, 0, 200) if isDarkTheme() else QColor(255, 255, 255))
            painter.drawText(self.view_rect, Qt.AlignmentFlag.AlignCenter, self.tr("view"))
            painter.setPen(themeColor())
            painter.drawText(self.delete_rect, Qt.AlignmentFlag.AlignCenter, self.tr("delete"))

        else:
            super().paintEvent(e)

    def enterEvent(self, e) -> None:
        self.lbl_project_name.setTextColor(themeColor())
        self.lbl_project_type.setVisible(False)
        self.lbl_create_time.setVisible(False)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.lbl_project_name.setTextColor()
        self.lbl_project_type.setVisible(True)
        self.lbl_create_time.setVisible(True)
        super().leaveEvent(e)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        mouse_pos = event.pos()
        if self.view_rect.contains(mouse_pos):
            self.is_hover_view = True
        else:
            self.is_hover_view = False
        if self.delete_rect.contains(mouse_pos):
            self.is_hover_delete = True
        else:
            self.is_hover_delete = False
        self.update()

    def mousePressEvent(self, e):
        # super().mousePressEvent(e)
        mouse_pos = e.pos()
        if self.view_rect.contains(mouse_pos):
            self.is_pressed_view = True
            self.update()
            self.view_clicked.emit()
        if self.delete_rect.contains(mouse_pos):
            self.is_pressed_delete = True
            self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.is_pressed_view = False
        self.is_pressed_delete = False
        self.update()

    def _delete_item(self):
        Path(cfg.get(cfg.workspace_folder)) / self.lbl_project_id.text()
