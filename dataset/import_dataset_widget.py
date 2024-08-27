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


class ImportDatasetWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("import_dataset")
        self.lbl_dataset_info = SubtitleLabel(self.tr("▌Dataset information"), self)
        self.lbl_dataset_id = BodyLabel()
        self.lbl_dataset_name = BodyLabel()
        self.lbl_dataset_dir = BodyLabel()
        self.tt_model_type = TextTagWidget()
        self.lbl_dataset_description = BodyLabel()
        self.lbl_dataset_description.setWordWrap(True)
        self.lbl_dataset_create_time = BodyLabel()
        self.file_select_widget = FileSelectWidget()

        self.fly_dataset_info = QFormLayout()
        self.fly_dataset_info.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.fly_dataset_info.setSpacing(20)

        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset ID:"), self), self.lbl_dataset_id)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset name:"), self), self.lbl_dataset_name)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset dir:"), self), self.lbl_dataset_dir)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Model type:"), self), self.tt_model_type)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset description:"), self),
                                     self.lbl_dataset_description)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Create time:"), self), self.lbl_dataset_create_time)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset Directory"), self), self.file_select_widget)
        self.btn_import = PrimaryPushButton(FluentIcon.DOWN, self.tr("Import"))
        self.btn_import.setMaximumWidth(200)
        self.fly_dataset_info.addRow("", self.btn_import)

        self.vly_dataset_info = QVBoxLayout()
        self.vly_dataset_info.addWidget(self.lbl_dataset_info)
        self.vly_dataset_info.addLayout(self.fly_dataset_info)
        # self.vly_dataset_info.addWidget(self.btn_import)
        self.vly_dataset_info.addStretch(1)

        self.dataset_format_doc_widget = DatasetFormatDocWidget()
        self.hly_content = QHBoxLayout(self)
        self.hly_content.addLayout(self.vly_dataset_info)
        self.hly_content.addWidget(self.dataset_format_doc_widget)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_import.clicked.connect(self._on_import_clicked)

    def _on_import_clicked(self):
        dataset_status = DatasetStatus.CHECK_FAILED
        if self._import_data():
            dataset_status = DatasetStatus.CHECKED
        core.EventManager().on_import_dataset_finished(self.lbl_dataset_id.text(), dataset_status)

    def _import_data(self):
        return True

    def set_dataset_info(self, dataset_info: DatasetInfo):
        if dataset_info.dataset_status == DatasetStatus.CHECK_FAILED:
            self.btn_import.setText(self.tr("Re import"))
        else:
            self.btn_import.setText(self.tr("Import"))
        self.lbl_dataset_id.setText(dataset_info.dataset_id)
        self.lbl_dataset_name.setText(dataset_info.dataset_name)
        self.tt_model_type.set_text(dataset_info.model_type.name)
        self.tt_model_type.set_color(dataset_info.model_type.color)
        self.lbl_dataset_description.setText(dataset_info.dataset_description)
        self.lbl_dataset_dir.setText(dataset_info.dataset_dir)
        self.lbl_dataset_create_time.setText(dataset_info.create_time)
        self.dataset_format_doc_widget.set_current_model_type(dataset_info.model_type)
