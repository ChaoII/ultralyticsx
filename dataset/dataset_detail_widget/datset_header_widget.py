from pathlib import Path

from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import SimpleCardWidget, SubtitleLabel, BodyLabel

from common.db_helper import db_session
from common.tag_widget import TextTagWidget
from dataset.dataset_checker.classify.split_dataset import split_dataset
from dataset.dataset_detail_widget.dataset_split_widget import DatasetSplitWidget
from dataset.types import DatasetInfo
from models.models import Dataset


class DatasetHeaderWidget(SimpleCardWidget):
    split_dataset_clicked = Signal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("dataset_detail")
        self.lbl_dataset_name = SubtitleLabel()
        self.tt_model_type = TextTagWidget()
        self.lbl_dataset_create_time = BodyLabel()
        self.dataset_header = DatasetSplitWidget()
        self.hly_dataset_info = QHBoxLayout()
        self.hly_dataset_info.setSpacing(30)
        self.hly_dataset_info.addWidget(self.lbl_dataset_name)
        self.hly_dataset_info.addWidget(self.tt_model_type)
        self.hly_dataset_info.addWidget(BodyLabel(self.tr("Create time:"), self))
        self.hly_dataset_info.addWidget(self.lbl_dataset_create_time)
        self.hly_dataset_info.addStretch(1)
        self.hly_dataset_info.addWidget(self.dataset_header)

        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.addLayout(self.hly_dataset_info)
        self._dataset_info = DatasetInfo()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.dataset_header.split_clicked.connect(self._on_split_clicked)

    @Slot(int, list)
    def set_dataset_header(self, dataset_total, split_rates):
        self.dataset_header.set_dataset(dataset_total, split_rates)

    @Slot(list)
    def _on_split_clicked(self, split_rates):
        self._split_rates = split_rates
        # 更新拆分比例
        dataset_df = split_dataset(Path(self._dataset_info.dataset_dir), self._split_rates)
        with db_session() as session:
            dataset = session.query(Dataset).filter_by(dataset_id=self._dataset_info.dataset_id).first()
            dataset.split_rate = "_".join([str(rate) for rate in split_rates])
            dataset.dataset_total = dataset_df.shape[0]
        self.split_dataset_clicked.emit(self._split_rates)

    def set_header_info(self, dataset_info: DatasetInfo):
        self._dataset_info = dataset_info
        self.lbl_dataset_name.setText("▌" + dataset_info.dataset_name)
        self.tt_model_type.set_text(dataset_info.model_type.name)
        self.tt_model_type.set_color(dataset_info.model_type.color)
        self.lbl_dataset_create_time.setText(dataset_info.create_time)
