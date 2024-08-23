from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout
from qfluentwidgets import BodyLabel, ComboBox, TitleLabel, SubtitleLabel, TextWrap, LineEdit

from common.file_select_widget1 import FileSelectWidget
from dataset.new_dataset_dialog import DatasetInfo


class ImportDatasetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("import_dataset")
        self.lbl_dataset_info = SubtitleLabel(self.tr("Dataset information"), self)
        self.lbl_dataset_id = BodyLabel()
        self.lbl_dataset_name = BodyLabel()
        self.lbl_dataset_dir = BodyLabel()
        self.lbl_dataset_description = BodyLabel()
        self.file_select_widget = FileSelectWidget()

        self.fly_dataset_info = QFormLayout()
        self.fly_dataset_info.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.fly_dataset_info.setSpacing(20)

        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset ID:"), self), self.lbl_dataset_id)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset name:"), self), self.lbl_dataset_name)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset dir:"), self), self.lbl_dataset_dir)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset description:"), self),
                                     self.lbl_dataset_description)
        self.fly_dataset_info.addRow(BodyLabel(self.tr("Dataset Directory"), self), self.file_select_widget)

        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.addWidget(self.lbl_dataset_info)
        self.vly_dataset_info.addLayout(self.fly_dataset_info)

        self.vly_dataset_info.addStretch(1)

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self.lbl_dataset_id.setText(dataset_info.dataset_id)
        self.lbl_dataset_name.setText(dataset_info.dataset_name)
        self.lbl_dataset_description.setText(TextWrap.wrap(dataset_info.dataset_description, 48, once=False)[0])
        self.lbl_dataset_dir.setText(dataset_info.dataset_dir)
