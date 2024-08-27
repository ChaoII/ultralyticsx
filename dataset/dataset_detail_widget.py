from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QFrame
from qfluentwidgets import BodyLabel, ComboBox, TitleLabel, SubtitleLabel, TextWrap, LineEdit, PrimaryPushButton, \
    FluentIcon, TextEdit, PlainTextEdit

from common.file_select_widget import FileSelectWidget
import core
from common.tag_widget import TextTagWidget
from common.utils import format_datatime
from dataset.dataset_format_doc_widget import DatasetFormatDocWidget

from dataset.new_dataset_dialog import DatasetInfo
from dataset.types import DatasetStatus
from common.collapsible_widget import CollapsibleWidget


class DatasetDetailWidget(QWidget):

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
        self.vly_dataset_info.addStretch(1)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        # self.btn_import.clicked.connect(self._on_import_clicked)l
        pass

    def _on_import_clicked(self):
        dataset_status = DatasetStatus.CHECK_FAILED
        if self._import_data():
            dataset_status = DatasetStatus.CHECKED
        core.EventManager().on_import_dataset_finished(self.lbl_dataset_id.text(), dataset_status)

    def _import_data(self):
        return True

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self.lbl_dataset_name.setText("▌" + dataset_info.dataset_name)
        self.tt_model_type.set_text(dataset_info.model_type.name)
        self.tt_model_type.set_color(dataset_info.model_type.color)
        self.lbl_dataset_create_time.setText(dataset_info.create_time)
