from ..common.dataset_draw_widget_base import DatasetDrawWidgetBase
from .detection_dataset_draw_thread import DetectionDatasetDrawThread


class DetectionDatasetDrawWidget(DatasetDrawWidgetBase):

    def __init__(self):
        super().__init__()

    def set_dataset_draw_thread(self):
        self.dataset_draw_thread = DetectionDatasetDrawThread()
