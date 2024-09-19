from dataset.dataset_detail_widget.classify.classify_dataset_draw_thread import ClassifyDatasetDrawThread
from dataset.dataset_detail_widget.common.dataset_draw_widget_base import DatasetDrawWidgetBase


class ClassifyDatasetDrawWidget(DatasetDrawWidgetBase):

    def __init__(self):
        super().__init__()

    def set_dataset_draw_thread(self):
        self.dataset_draw_thread = ClassifyDatasetDrawThread()
