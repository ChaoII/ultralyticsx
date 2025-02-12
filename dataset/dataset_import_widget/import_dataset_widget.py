from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, SubtitleLabel, PrimaryPushButton, \
    InfoBar, InfoBarPosition

from common.component.custom_icon import CustomFluentIcon
from common.component.file_select_widget import FileSelectWidget
from common.core.event_manager import signal_bridge
from common.component.tag_widget import TextTagWidget
from common.utils.utils import copy_tree
from ..dataset_process import check_dataset
from dataset.dataset_import_widget.dataset_format_doc_widget import DatasetFormatDocWidget

from dataset.dataset_list_widget.new_dataset_dialog import DatasetInfo
from dataset.types import DatasetStatus


class ImportDatasetWidget(QWidget):
    check_and_import_finished = Signal(DatasetInfo)

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
        self.btn_import = PrimaryPushButton(CustomFluentIcon.IMPORT1, self.tr("Import"))
        self.btn_import.setFixedWidth(140)

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
        self.fly_dataset_info.addRow("", self.btn_import)

        self.vly_dataset_info = QVBoxLayout()
        self.vly_dataset_info.addWidget(self.lbl_dataset_info)
        self.vly_dataset_info.addLayout(self.fly_dataset_info)
        self.vly_dataset_info.addStretch(1)

        self.dataset_format_doc_widget = DatasetFormatDocWidget()
        self.hly_content = QHBoxLayout(self)
        self.hly_content.addLayout(self.vly_dataset_info)
        self.hly_content.addWidget(self.dataset_format_doc_widget)
        self._selected_dataset_dir = ""
        self._dataset_info = DatasetInfo()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_import.clicked.connect(self._on_import_clicked)
        self.file_select_widget.path_selected.connect(self._on_dataset_path_selected)

    @Slot(str)
    def _on_dataset_path_selected(self, file_path):
        self._selected_dataset_dir = file_path

    def _on_import_clicked(self):
        if self._import_data():
            signal_bridge.import_dataset_finished.emit(self.lbl_dataset_id.text(), DatasetStatus.CHECKED.value)
            self.check_and_import_finished.emit(self._dataset_info)
        else:
            signal_bridge.import_dataset_finished.emit(self.lbl_dataset_id.text(), DatasetStatus.CHECK_FAILED.value)

    def _import_data(self):
        if not self._selected_dataset_dir:
            InfoBar.error(title='', content=self.tr("Please select a dataset directory!"),
                          orient=Qt.Orientation.Vertical, isClosable=True, position=InfoBarPosition.TOP_RIGHT,
                          duration=2000, parent=self)
            return False
        if not check_dataset(Path(self._selected_dataset_dir), self._dataset_info.model_type):
            InfoBar.error(title='', content=self.tr("Dataset format error, please check your dataset!"),
                          orient=Qt.Orientation.Vertical, isClosable=True, position=InfoBarPosition.TOP_RIGHT,
                          duration=2000, parent=self)
            return False
        else:
            copy_tree(self._selected_dataset_dir, Path(self._dataset_info.dataset_dir) / "src")
            # 跳转拆分界面并且显示数据
            return True

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self._dataset_info = dataset_info
        if dataset_info.dataset_status == DatasetStatus.CHECK_FAILED:
            self.btn_import.setText(self.tr("Re import"))
        else:
            self.btn_import.setText(self.tr("Import"))
        self.lbl_dataset_id.setText(dataset_info.dataset_id)
        self.lbl_dataset_name.setText(dataset_info.dataset_name)
        self.tt_model_type.set_text(dataset_info.model_type.name)
        self.tt_model_type.set_color(*dataset_info.model_type.color)
        self.lbl_dataset_description.setText(dataset_info.dataset_description)
        self.lbl_dataset_dir.setText(dataset_info.dataset_dir)
        self.lbl_dataset_create_time.setText(dataset_info.create_time)
        self.dataset_format_doc_widget.set_current_model_type(dataset_info.model_type)
