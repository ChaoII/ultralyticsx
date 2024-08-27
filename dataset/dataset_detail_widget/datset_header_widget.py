from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import SimpleCardWidget, SubtitleLabel, BodyLabel

import core
from common.tag_widget import TextTagWidget
from dataset.types import DatasetStatus, DatasetInfo


class DatasetHeaderWidget(SimpleCardWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("dataset_detail")
        self.lbl_dataset_name = SubtitleLabel()
        self.tt_model_type = TextTagWidget()
        self.lbl_dataset_create_time = BodyLabel()

        self.hly_dataset_info = QHBoxLayout()
        self.hly_dataset_info.setSpacing(30)
        self.hly_dataset_info.addWidget(self.lbl_dataset_name)
        self.hly_dataset_info.addWidget(self.tt_model_type)
        self.hly_dataset_info.addWidget(BodyLabel(self.tr("Create time:"), self))
        self.hly_dataset_info.addWidget(self.lbl_dataset_create_time)
        self.hly_dataset_info.addStretch(1)

        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.addLayout(self.hly_dataset_info)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        # self.btn_import.clicked.connect(self._on_import_clicked)
        pass

    def _on_import_clicked(self):
        dataset_status = DatasetStatus.CHECK_FAILED
        if self._import_data():
            dataset_status = DatasetStatus.CHECKED
        core.EventManager().on_import_dataset_finished(self.lbl_dataset_id.text(), dataset_status)

    def _import_data(self):
        return True

    def set_header_info(self, dataset_info: DatasetInfo):
        self.lbl_dataset_name.setText("▌" + dataset_info.dataset_name)
        self.tt_model_type.set_text(dataset_info.model_type.name)
        self.tt_model_type.set_color(dataset_info.model_type.color)
        self.lbl_dataset_create_time.setText(dataset_info.create_time)
