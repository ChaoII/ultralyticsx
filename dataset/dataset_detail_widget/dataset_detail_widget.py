from PySide6.QtWidgets import QWidget, QVBoxLayout

from dataset.dataset_detail_widget.dataset_detail_classify_widget import ClassifyDataset
from dataset.dataset_detail_widget.datset_header_widget import DatasetHeaderWidget
from dataset.new_dataset_dialog import DatasetInfo
from dataset.types import DatasetStatus


class DatasetDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vly = QVBoxLayout(self)
        self.header = DatasetHeaderWidget()
        self.content = ClassifyDataset()
        self.vly.addWidget(self.header)
        self.vly.addWidget(self.content)
        # self.vly.addStretch(1)
        self._dataset_info: DatasetInfo | None = None
        self._is_split = False

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self.header.set_header_info(dataset_info)
        self.content.set_dataset_info(dataset_info)
        self._dataset_info = dataset_info
