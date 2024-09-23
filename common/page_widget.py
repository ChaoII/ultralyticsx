from enum import Enum
from functools import singledispatch, update_wrapper

from PySide6.QtCore import Qt, Signal, QModelIndex, Property, QSize, QRectF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (QStyleOptionViewItem, QStyle, QListWidget, QListWidgetItem, QStyledItemDelegate)
from qfluentwidgets import FluentIcon, drawIcon, isDarkTheme, FluentStyleSheet, ToolButton, ToolTipFilter, \
    ToolTipPosition, SmoothScrollBar, themeColor


class singledispatchmethod:
    """Single-dispatch generic method descriptor.

    Supports wrapping existing descriptors and handles non-descriptor
    callables as instance methods.
    """

    def __init__(self, func):
        if not callable(func) and not hasattr(func, "__get__"):
            raise TypeError(f"{func!r} is not callable or a descriptor")

        self.dispatcher = singledispatch(func)
        self.func = func

    def register(self, cls, method=None):
        """generic_method.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_method*.
        """
        return self.dispatcher.register(cls, func=method)

    def __get__(self, obj, cls=None):
        def _method(*args, **kwargs):
            if args:
                method = self.dispatcher.dispatch(args[0].__class__)
            else:
                method = self.func
                for v in kwargs.values():
                    if v.__class__ in self.dispatcher.registry:
                        method = self.dispatcher.dispatch(v.__class__)
                        if method is not self.func:
                            break

            return method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        return _method

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)


class PipsScrollButtonDisplayMode(Enum):
    """ Pips pager scroll button display mode """
    ALWAYS = 0
    ON_HOVER = 1
    NEVER = 2


class ScrollButton(ToolButton):
    """ Scroll button """

    def _postInit(self):
        self.setFixedSize(30, 30)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if isDarkTheme():
            color = QColor(255, 255, 255)
            painter.setOpacity(0.773 if self.isHover or self.isPressed else 0.541)
        else:
            color = QColor(0, 0, 0)
            painter.setOpacity(0.616 if self.isHover or self.isPressed else 0.45)

        if self.isPressed:
            rect = QRectF(3, 3, 20, 20)
        else:
            rect = QRectF(5, 5, 20, 20)

        drawIcon(self._icon, painter, rect, fill=color.name())


class PipsDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hovered_row = -1
        self.pressed_row = -1

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        is_hover = index.row() == self.hovered_row
        is_pressed = index.row() == self.pressed_row
        # draw pip
        if option.state & QStyle.StateFlag.State_Selected or (is_hover and not is_pressed):
            r = themeColor().red()
            g = themeColor().green()
            b = themeColor().blue()
            if isDarkTheme():
                if is_hover or is_pressed:
                    color = QColor(r, g, b, 197)
                else:
                    color = QColor(r, g, b, 138)
            else:
                if is_hover or is_pressed:
                    color = QColor(r, g, b, 157)
                else:
                    color = QColor(r, g, b, 114)
            painter.setBrush(color)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        rect = option.rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 5, 5)
        page_num = index.row() + 1
        painter.setPen(QColor(255, 255, 255, 197) if isDarkTheme() else QColor(0, 0, 0, 200))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(page_num))
        painter.restore()

    def setPressedRow(self, row: int):
        self.pressed_row = row
        self.parent().viewport().update()

    def setHoveredRow(self, row: int):
        self.hovered_row = row
        self.parent().viewport().update()


class PipsPager(QListWidget):
    """ Pips pager

    Constructors
    ------------
    * PipsPager(`parent`: QWidget = None)
    * PipsPager(`orient`: Qt.Orientation, `parent`: QWidget = None)
    """

    currentIndexChanged = Signal(int)

    @singledispatchmethod
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._postInit()

    def _postInit(self):
        self._visibleNumber = 5
        self.isHover = False

        self.delegate = PipsDelegate(self)
        self.scrollBar = SmoothScrollBar(Qt.Orientation.Horizontal, self)

        self.scrollBar.setScrollAnimation(500)
        self.scrollBar.setForceHidden(True)

        self.setMouseTracking(True)
        self.setUniformItemSizes(True)
        self.setGridSize(QSize(30, 30))
        self.setItemDelegate(self.delegate)
        self.setMovement(QListWidget.Movement.Static)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        FluentStyleSheet.PIPS_PAGER.apply(self)

        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setViewportMargins(30, 0, 30, 0)
        self.preButton = ScrollButton(FluentIcon.CARE_LEFT_SOLID, self)
        self.nextButton = ScrollButton(FluentIcon.CARE_RIGHT_SOLID, self)

        self.setFixedHeight(30)

        self.preButton.installEventFilter(ToolTipFilter(self.preButton, 1000, ToolTipPosition.LEFT))
        self.nextButton.installEventFilter(ToolTipFilter(self.nextButton, 1000, ToolTipPosition.RIGHT))

        self.setPreviousButtonDisplayMode(PipsScrollButtonDisplayMode.NEVER)
        self.setNextButtonDisplayMode(PipsScrollButtonDisplayMode.NEVER)
        self.preButton.setToolTip(self.tr('Previous Page'))
        self.nextButton.setToolTip(self.tr('Next Page'))

        # connect signal to slot
        self.preButton.clicked.connect(self.scrollPrevious)
        self.nextButton.clicked.connect(self.scrollNext)
        self.itemPressed.connect(self._setPressedItem)
        self.itemEntered.connect(self._setHoveredItem)

    def _setPressedItem(self, item: QListWidgetItem):
        self.delegate.setPressedRow(self.row(item))
        self.setCurrentIndex(self.row(item))

    def _setHoveredItem(self, item: QListWidgetItem):
        self.delegate.setHoveredRow(self.row(item))

    def setPageNumber(self, n: int):
        """ set the number of page """
        self.clear()
        self.addItems([''] * n)

        for i in range(n):
            item = self.item(i)
            item.setData(Qt.ItemDataRole.UserRole, i + 1)
            item.setSizeHint(QSize(30, 30))

        self.setCurrentIndex(0)
        self.adjustSize()

    def getPageNumber(self):
        """ get the number of page """
        return self.count()

    def getVisibleNumber(self):
        """ get the number of visible pips """
        return self._visibleNumber

    def setVisibleNumber(self, n: int):
        self._visibleNumber = n
        self.adjustSize()

    def scrollNext(self):
        """ scroll down an item """
        self.setCurrentIndex(self.currentIndex() + 1)

    def scrollPrevious(self):
        """ scroll up an item """
        self.setCurrentIndex(self.currentIndex() - 1)

    def scrollToItem(self, item: QListWidgetItem, hint=QListWidget.ScrollHint.PositionAtCenter):
        """ scroll to item """
        # scroll to center position
        index = self.row(item)
        size = item.sizeHint()
        self.scrollBar.scrollTo(self.gridSize().width() * (index - self.visibleNumber // 2))

        # clear selection
        self.clearSelection()
        item.setSelected(False)

        self.currentIndexChanged.emit(index)

    def adjustSize(self) -> None:
        m = self.viewportMargins()
        w = self.visibleNumber * self.gridSize().width() + m.left() + m.right()
        self.setFixedWidth(w)

    def setCurrentIndex(self, index: int):
        """ set current index """
        if not 0 <= index < self.count():
            return

        item = self.item(index)
        self.scrollToItem(item)
        super().setCurrentItem(item)
        self._updateScrollButtonVisibility()

    def isPreviousButtonVisible(self):
        if self.currentIndex() <= 0 or self.previousButtonDisplayMode == PipsScrollButtonDisplayMode.NEVER:
            return False

        if self.previousButtonDisplayMode == PipsScrollButtonDisplayMode.ON_HOVER:
            return self.isHover

        return True

    def isNextButtonVisible(self):
        if self.currentIndex() >= self.count() - 1 or self.nextButtonDisplayMode == PipsScrollButtonDisplayMode.NEVER:
            return False

        if self.nextButtonDisplayMode == PipsScrollButtonDisplayMode.ON_HOVER:
            return self.isHover

        return True

    def currentIndex(self) -> int:
        return super().currentIndex().row()

    def setPreviousButtonDisplayMode(self, mode: PipsScrollButtonDisplayMode):
        """ set the display mode of previous button """
        self.previousButtonDisplayMode = mode
        self.preButton.setVisible(self.isPreviousButtonVisible())

    def setNextButtonDisplayMode(self, mode: PipsScrollButtonDisplayMode):
        """ set the display mode of next button """
        self.nextButtonDisplayMode = mode
        self.nextButton.setVisible(self.isNextButtonVisible())

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.delegate.setPressedRow(-1)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isHover = True
        self._updateScrollButtonVisibility()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isHover = False
        self.delegate.setHoveredRow(-1)
        self._updateScrollButtonVisibility()

    def _updateScrollButtonVisibility(self):
        self.preButton.setVisible(self.isPreviousButtonVisible())
        self.nextButton.setVisible(self.isNextButtonVisible())

    def wheelEvent(self, e):
        pass

    def resizeEvent(self, e):
        w, h = self.width(), self.height()
        bw, bh = self.preButton.width(), self.preButton.height()
        self.preButton.move(0, int(h / 2 - bh / 2))
        self.nextButton.move(w - bw, int(h / 2 - bh / 2))

    visibleNumber = Property(int, getVisibleNumber, setVisibleNumber)
    pageNumber = Property(int, getPageNumber, setPageNumber)
