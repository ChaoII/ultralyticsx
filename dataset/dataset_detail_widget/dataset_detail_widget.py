from PySide6.QtWidgets import QWidget, QVBoxLayout

from common.model_type_widget import ModelType
from .classify.classify_dataset_detail_widget import ClassifyDatasetDetailWidget
from .detection.detection_dataset_detail_widget import DetectionDatasetDetailWidget
from dataset.dataset_detail_widget.common.datset_header_widget import DatasetHeaderWidget
from dataset.dataset_list_widget.new_dataset_dialog import DatasetInfo
from .common.dataset_detail_widget_base import DatasetDetailWidgetBase


class DatasetDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vly = QVBoxLayout(self)
        self.header = DatasetHeaderWidget()
        self.content: DatasetDetailWidgetBase | None = None
        self.vly.addWidget(self.header)
        # self.vly.addWidget(self.content)
        # self.vly.addStretch(1)
        self._dataset_info: DatasetInfo | None = None
        self._is_split = False

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self.header.set_header_info(dataset_info)
        self._dataset_info = dataset_info

        if self.content:
            self.vly.removeWidget(self.content)
            self.content.deleteLater()

        if self._dataset_info.model_type == ModelType.CLASSIFY:
            self.content = ClassifyDatasetDetailWidget()
        elif self._dataset_info.model_type == ModelType.DETECTION:
            self.content = DetectionDatasetDetailWidget()
        else:
            return

        self.vly.addWidget(self.content)
        self.content.set_dataset_info(dataset_info)
        self.content.load_dataset_finished.connect(self.header.set_dataset_header)
        self.header.split_dataset_clicked.connect(self.content.split_dataset)
