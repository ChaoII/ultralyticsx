from .obb_dataset_draw_widget import OBBDatasetDrawWidget
from ..common.dataset_detail_widget_base import DatasetDetailWidgetBase


class OBBDatasetDetailWidget(DatasetDetailWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("detect_dataset")

    def set_draw_widget(self):
        draw_widget = OBBDatasetDrawWidget()
        self.draw_widget = draw_widget
        self.hly_content.addWidget(draw_widget)
