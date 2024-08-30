from PySide6.QtWidgets import QWidget, QVBoxLayout

from dataset.dataset_detail_widget.classify.dataset_detail_classify_widget import ClassifyDataset
from dataset.dataset_detail_widget.common.datset_header_widget import DatasetHeaderWidget
from dataset.dataset_list_widget.new_dataset_dialog import DatasetInfo


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

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.header.split_dataset_clicked.connect(self.content.split_dataset)
        self.content.load_dataset_finished.connect(self.header.set_dataset_header)

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self.header.set_header_info(dataset_info)
        self.content.set_dataset_info(dataset_info)
        self._dataset_info = dataset_info
