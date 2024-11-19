from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtWidgets import QFormLayout
from qfluentwidgets import SimpleCardWidget, CompactSpinBox, BodyLabel


class ItemPropertyWidgetBase(SimpleCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(0)
        self.animation = QPropertyAnimation(self, b"width_")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_collapse = True

    @Property(int)
    def width_(self):
        return self.width()

    @width_.setter
    def width_(self, value):
        self.setFixedWidth(value)

    def on_btn_collapse_clicked(self):
        if self.minimumWidth() == 0:
            self.animation.setStartValue(0)
            self.animation.setEndValue(200)
            self.is_collapse = False
        else:
            self.animation.setStartValue(200)
            self.animation.setEndValue(0)
            self.is_collapse = True
        self.animation.start()


class RectItemPropertyWidget(ItemPropertyWidgetBase):
    shape_changed = Signal(int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        fly_content = QFormLayout(self)
        self.spb_x = CompactSpinBox()
        self.spb_x.setRange(0, 10000)
        self.spb_x.setValue(100)

        self.spb_y = CompactSpinBox()
        self.spb_y.setRange(0, 10000)
        self.spb_y.setValue(100)

        self.spb_w = CompactSpinBox()
        self.spb_w.setRange(0, 10000)
        self.spb_w.setValue(100)

        self.spb_h = CompactSpinBox()
        self.spb_h.setRange(0, 10000)
        self.spb_h.setValue(100)

        fly_content.addRow(BodyLabel("x:", self), self.spb_x)
        fly_content.addRow(BodyLabel("y:", self), self.spb_y)
        fly_content.addRow(BodyLabel("w:", self), self.spb_w)
        fly_content.addRow(BodyLabel("h:", self), self.spb_h)

        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self.spb_x.valueChanged.connect(self.on_x_changed)
        self.spb_y.valueChanged.connect(self.on_y_changed)
        self.spb_w.valueChanged.connect(self.on_w_changed)
        self.spb_h.valueChanged.connect(self.on_h_changed)

    def on_x_changed(self, x):
        self.x = x
        self.shape_changed.emit(self.x, self.y, self.w, self.h)

    def on_y_changed(self, y):
        self.y = y
        self.shape_changed.emit(self.x, self.y, self.w, self.h)

    def on_w_changed(self, w):
        self.w = w
        self.shape_changed.emit(self.x, self.y, self.w, self.h)

    def on_h_changed(self, h):
        self.h = h
        self.shape_changed.emit(self.x, self.y, self.w, self.h)
