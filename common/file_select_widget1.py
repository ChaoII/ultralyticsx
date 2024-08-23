from pathlib import Path

from PySide6.QtCore import QSize, QRectF, QRect, QPoint, Qt, QEvent
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QEnterEvent, QMouseEvent, QCursor
from PySide6.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import themeColor, LineEdit
from qfluentwidgets.common.icon import toQIcon, drawIcon, FluentIcon


class FileSelectWidget(LineEdit):
    """ Scroll button """

    def __init__(self, is_dir=True):
        super().__init__()
        self.setMouseTracking(True)
        self._icon = FluentIcon.DICTIONARY
        self.setMinimumSize(240, 32)
        self._icon_size = QSize(16, 16)
        self._icon_rect = None
        self._text_rect = None
        self._is_pressed = False
        self._is_hovered = False
        self._cur_text = ""
        self.is_dir = is_dir
        self.setReadOnly(True)

    def _fit_width(self):
        # 获取字体大小
        font = QFont()
        fm = QFontMetrics(font)
        self.text_width = fm.boundingRect(self._cur_text).width()

    def setIconSize(self, size: QSize):
        self._icon_size = size
        self._fit_width()

    def iconSize(self) -> QSize:
        return self._icon_size

    def icon(self):
        return toQIcon(self._icon)

    def paintEvent(self, e):
        super(FileSelectWidget, self).paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        icon_color = themeColor()
        icon_rect = self._icon_rect = QRect(self.width() - self._icon_size.width() - 8,
                                            (self.height() - self._icon_size.width()) // 2,
                                            self._icon_size.width(), self._icon_size.height())
        if self._is_hovered:
            icon_color = themeColor().darker(200)

        # 按下的瞬间就会弹出窗口，所以可以禁用按下的样式
        # if self._is_pressed:
        #     icon_color = themeColor().darker(150)
        #     icon_rect.adjust(1, 1, 1, 1)

        drawIcon(self._icon, painter, icon_rect, fill=icon_color.name())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        mouse_pos = event.pos()
        if self._icon_rect.contains(mouse_pos):
            self._is_hovered = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self._is_hovered = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        mouse_pos = event.pos()
        if self._icon_rect.contains(mouse_pos):
            self._is_pressed = True
            self._open_directory()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self._is_pressed = False

    def _open_directory(self):
        if self.is_dir:
            directory = QFileDialog.getExistingDirectory(self, self.tr("Select a directory"), Path.home().as_posix())
            if directory:
                self._cur_text = directory
        else:
            filename, _ = QFileDialog.getOpenFileName(self, self.tr("Select a file"), ".")
            self._cur_text = filename

        self.setText(self._cur_text)
