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

##### 数据标注格式说明(坐标都经过归一化处理)

- 检测数据

```
class_id,x_center,y_center,width,height
```

- 实例分割

```
class_id x1,y1,x2,y2,...xn,yn
```

- obb

```
class_id,x1,y1,x2,y2,x3,y3,x4,y4
```

- pose

```
class_id,x_center,y_center,width,height,x1,y1,v1,x2,y2,v2,...x17,y17,v17
```


##### 路线图
- [x] 增加标注框的复制粘贴功能
- [x] 增加标注框的对齐功能
- [x] 增加半自动标注功能
- [ ] 界面增加中文翻译
- [ ] 支持yolov11