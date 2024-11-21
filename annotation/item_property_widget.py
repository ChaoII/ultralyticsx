from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtWidgets import QFormLayout, QSpinBox, QVBoxLayout
from qfluentwidgets import SimpleCardWidget, CompactSpinBox, BodyLabel, LineEdit


class ItemPropertyWidgetBase(SimpleCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(0)
        self.animation = QPropertyAnimation(self, b"width_")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_collapse = True
        self.vly_content = QVBoxLayout(self)
        self.lbl_id = BodyLabel("id:", self)
        self.lbl_annotation = BodyLabel("annotation:", self)
        self.le_id = LineEdit()
        self.le_id.setReadOnly(True)
        self.le_annotation = LineEdit()
        self.le_annotation.setReadOnly(True)
        self.vly_content.addWidget(self.lbl_id)
        self.vly_content.addWidget(self.le_id)
        self.vly_content.addWidget(self.lbl_annotation)
        self.vly_content.addWidget(self.le_annotation)

    def set_id(self, annotation_id: str):
        self.le_id.setText(annotation_id)

    def set_annotation(self, annotation: str):
        self.le_annotation.setText(annotation)

    def update_property(self, shape_data: list):
        raise NotImplementedError

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
        fly_content = QFormLayout()

        self.spb_x = CompactSpinBox()
        self.spb_x.setRange(0, 10000)
        self.spb_x.setValue(0)

        self.spb_y = CompactSpinBox()
        self.spb_y.setRange(0, 10000)
        self.spb_y.setValue(0)

        self.spb_w = CompactSpinBox()
        self.spb_w.setRange(0, 10000)
        self.spb_w.setValue(0)

        self.spb_h = CompactSpinBox()
        self.spb_h.setRange(0, 10000)
        self.spb_h.setValue(0)

        fly_content.addRow(BodyLabel("x:", self), self.spb_x)
        fly_content.addRow(BodyLabel("y:", self), self.spb_y)
        fly_content.addRow(BodyLabel("w:", self), self.spb_w)
        fly_content.addRow(BodyLabel("h:", self), self.spb_h)
        self.vly_content.addLayout(fly_content)
        self.vly_content.addStretch(1)

        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

        self.connect_signals_and_slots()

    def update_property(self, shape_data: list):
        x_c, y_c, w, h = shape_data
        self.set_x(int(x_c - w / 2))
        self.set_y(int(y_c - h / 2))
        self.set_w(int(w))
        self.set_h(int(h))

    def set_x(self, x: int):
        self.spb_x.setValue(x)
        self.x = x

    def set_y(self, y: int):
        self.spb_y.setValue(y)
        self.y = y

    def set_w(self, w: int):
        self.spb_w.setValue(w)
        self.w = w

    def set_h(self, h: int):
        self.spb_h.setValue(h)
        self.h = h

    def connect_signals_and_slots(self):
        self.spb_x.valueChanged.connect(self.on_x_changed)
        self.spb_y.valueChanged.connect(self.on_y_changed)
        self.spb_w.valueChanged.connect(self.on_w_changed)
        self.spb_h.valueChanged.connect(self.on_h_changed)

    def on_x_changed(self, x):
        self.x = int(x)
        self.shape_changed.emit(self.x, self.y, self.w, self.h)

    def on_y_changed(self, y):
        self.y = int(y)
        self.shape_changed.emit(self.x, self.y, self.w, self.h)

    def on_w_changed(self, w):
        self.w = int(w)
        self.shape_changed.emit(self.x, self.y, self.w, self.h)

    def on_h_changed(self, h):
        self.h = int(h)
        self.shape_changed.emit(self.x, self.y, self.w, self.h)
