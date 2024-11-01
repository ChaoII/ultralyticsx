from .segment_dataset_draw_widget import SegmentDatasetDrawWidget
from ..common.dataset_detail_widget_base import DatasetDetailWidgetBase


class SegmentDatasetDetailWidget(DatasetDetailWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("detect_dataset")

    def set_draw_widget(self):
        draw_widget = SegmentDatasetDrawWidget()
        self.draw_widget = draw_widget
        self.hly_content.addWidget(draw_widget)

