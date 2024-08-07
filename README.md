# ultralyticsx

##### 绘制圆角QWidget（最外层）

```python
from PySide6.QtGui import QPainterPath, QRegion


def set_border_radius(self, radius: float):
    path = QPainterPath()
    path.addRoundedRect(self.rect(), radius, radius)
    mask = QRegion(path.toFillPolygon().toPolygon())
    self.setMask(mask)
```