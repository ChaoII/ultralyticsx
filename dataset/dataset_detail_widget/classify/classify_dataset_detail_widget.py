from dataset.dataset_detail_widget.classify.classify_dataset_draw_widget import ClassifyDatasetDrawWidget
from dataset.dataset_detail_widget.common.dataset_detail_widget_base import DatasetDetailWidgetBase


class ClassifyDatasetDetailWidget(DatasetDetailWidgetBase):
    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")

    def set_draw_widget(self):
        draw_widget = ClassifyDatasetDrawWidget()
        self.draw_widget = draw_widget
        self.hly_content.addWidget(draw_widget)
