from PySide6.QtCore import Qt, Signal, QSize, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QFrame, QAbstractItemView, QHeaderView, \
    QTableWidgetItem, QGridLayout
from qfluentwidgets import BodyLabel, ComboBox, TitleLabel, SubtitleLabel, TextWrap, LineEdit, PrimaryPushButton, \
    FluentIcon, TextEdit, PlainTextEdit, SimpleCardWidget, FlyoutViewBase, TransparentToolButton, InfoBarIcon, \
    StrongBodyLabel, PushButton, PopupTeachingTip, TeachingTipTailPosition, TableWidget, themeColor, HyperlinkLabel, \
    CompactSpinBox

from common.custom_label_widget import CustomLabel
from common.file_select_widget import FileSelectWidget
import core
from common.tag_widget import TextTagWidget
from common.utils import format_datatime
from dataset.dataset_format_doc_widget import DatasetFormatDocWidget

from dataset.new_dataset_dialog import DatasetInfo
from dataset.types import DatasetStatus
from common.collapsible_widget import CollapsibleWidget


class SplitDatasetContentWidget(QWidget):
    rate_changed = Signal(list)

    def __init__(self, total_dataset: int):
        super().__init__()

        self.lbl_type = BodyLabel(self.tr("Type"), self)
        self.lbl_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_training_set = BodyLabel(self.tr("Training set"), self)
        self.lbl_training_set.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_validation_set = BodyLabel(self.tr("Validation set"), self)
        self.lbl_validation_set.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_testing_set = BodyLabel(self.tr("Testing set"), self)
        self.lbl_testing_set.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_rate = BodyLabel(self.tr("Rate(%)"), self)
        self.lbl_rate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.csb_training_rate = CompactSpinBox()
        self._training_rate = 70
        self.csb_training_rate.setValue(self._training_rate)
        self.csb_training_rate.setRange(0, 100)

        self.csb_validation_rate = CompactSpinBox()
        self._validation_rate = 20
        self.csb_validation_rate.setValue(self._validation_rate)
        self.csb_validation_rate.setRange(0, 100)

        self.csb_testing_rate = CompactSpinBox()
        self._testing_rate = 10
        self.csb_testing_rate.setValue(self._testing_rate)
        self.csb_testing_rate.setRange(0, 100)

        self.lbl_num = BodyLabel(self.tr("Number"), self)
        self.lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_training_num = BodyLabel()
        self.lbl_validation_num = BodyLabel()
        self.lbl_testing_num = BodyLabel()
        self.lbl_training_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_validation_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_testing_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gly = QGridLayout(self)

        self.gly.addWidget(self.lbl_type, 0, 0)
        self.gly.addWidget(self.lbl_training_set, 0, 1)
        self.gly.addWidget(self.lbl_validation_set, 0, 2)
        self.gly.addWidget(self.lbl_testing_set, 0, 3)

        self.gly.addWidget(self.lbl_rate, 1, 0)
        self.gly.addWidget(self.csb_training_rate, 1, 1)
        self.gly.addWidget(self.csb_validation_rate, 1, 2)
        self.gly.addWidget(self.csb_testing_rate, 1, 3)

        self.gly.addWidget(self.lbl_num, 2, 0)
        self.gly.addWidget(self.lbl_training_num, 2, 1)
        self.gly.addWidget(self.lbl_validation_num, 2, 2)
        self.gly.addWidget(self.lbl_testing_num, 2, 3)

        self.total_dataset = total_dataset
        self._training_num = int(self.total_dataset * self._training_rate / 100)
        self._validation_num = int(self.total_dataset * self._validation_rate / 100)
        self._testing_num = int(self.total_dataset * self._testing_rate / 100)
        self.update_num()

        self._connect_signals_and_slots()

    def set_total_dataset(self, total_dataset: int):
        self.total_dataset = total_dataset
        self.update_num()

    def _connect_signals_and_slots(self):
        self.csb_training_rate.valueChanged.connect(lambda value: self._on_rate_value_changed(0, value))
        self.csb_validation_rate.valueChanged.connect(lambda value: self._on_rate_value_changed(1, value))
        self.csb_testing_rate.valueChanged.connect(lambda value: self._on_rate_value_changed(2, value))

    def _on_rate_value_changed(self, index: int, value: int):
        if index == 0:
            self._training_rate = value
        if index == 1:
            self._validation_rate = value
        if index == 2:
            self._testing_rate = value
        self.update_num()

        self.rate_changed.emit([self._training_num, self._validation_num, self._testing_num])

    def update_num(self):
        self._training_num = int(self.total_dataset * self._training_rate / 100)
        self._validation_num = int(self.total_dataset * self._validation_rate / 100)
        self._testing_num = int(self.total_dataset * self._testing_rate / 100)

        self.lbl_training_num.setText(str(self._training_num))
        self.lbl_validation_num.setText(str(self._validation_num))
        self.lbl_testing_num.setText(str(self._testing_num))


class DatasetSplitFlyoutView(FlyoutViewBase):
    def addWidget(self, widget: QWidget, stretch=0, align=Qt.AlignmentFlag.AlignLeft):
        pass

    accept_status = Signal(bool, list)

    def __init__(self, total_datasets: int, parent=None):
        super().__init__(parent)
        self.setFixedWidth(440)
        self.vBoxLayout = QVBoxLayout(self)
        self.lbl_title = StrongBodyLabel(self.tr("Dataset split"), self)
        self.icon = TransparentToolButton(InfoBarIcon.WARNING, parent=self)
        self.icon.setIconSize(QSize(20, 20))
        self.lbl_tips = CustomLabel(self.tr("Tip: The sum of three datasets must be 100%, "
                                            "the test set can be 0, and the validation set cannot be 0"), self)
        self.lbl_tips.setWordWrap(True)
        self.lbl_tips.setTextColor(themeColor(), themeColor())

        self.btn_ensure = PrimaryPushButton(self.tr('Split'), self)
        self.btn_cancel = PushButton(self.tr("Cancel"), self)
        self.btn_ensure.setFixedWidth(120)
        self.btn_cancel.setFixedWidth(120)
        self.hly_content = QHBoxLayout()
        self.hly_content.addWidget(self.icon)
        self.hly_content.addWidget(self.lbl_tips)

        self.split_dataset_content_widget = SplitDatasetContentWidget(total_datasets)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addStretch(1)
        self.hly_btn.addWidget(self.btn_ensure)
        self.hly_btn.addWidget(self.btn_cancel)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(self.lbl_title)
        self.vBoxLayout.addLayout(self.hly_content)
        self.vBoxLayout.addWidget(self.split_dataset_content_widget)
        self.vBoxLayout.addLayout(self.hly_btn)

        self.split_nums = []
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_ensure.clicked.connect(lambda: self.accept_status.emit(True, self.split_nums))
        self.btn_cancel.clicked.connect(lambda: self.accept_status.emit(False, self.split_nums))
        self.split_dataset_content_widget.rate_changed.emit(self._on_rate_changed)

    @Slot(list)
    def _on_rate_changed(self, split_nums: list):
        self.split_nums = split_nums


class ClassifyDataset(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("classify_dataset")
        self.lbl_title = SubtitleLabel("▌" + self.tr("Data analysis"), self)

        self.lbl_split_tip = BodyLabel(self.tr("Dataset have split, you can split again"), self)
        self.btn_split = HyperlinkLabel(self.tr("Split again"))
        self.btn_split.setUnderlineVisible(True)

        self.hly_dataset_info = QHBoxLayout()
        self.hly_dataset_info.setSpacing(30)
        self.hly_dataset_info.addWidget(self.lbl_title)
        self.hly_dataset_info.addWidget(self.lbl_split_tip)
        self.hly_dataset_info.addWidget(self.btn_split)
        self.hly_dataset_info.addStretch(1)

        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.addLayout(self.hly_dataset_info)

        self._split_nums = []
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_split.clicked.connect(self._on_split_clicked)

    def _import_data(self):
        return True

    def _on_split_clicked(self):
        self.view = DatasetSplitFlyoutView(content=self.tr("Are you sure to delete this dataset?"))
        self.popup_tip = PopupTeachingTip.make(
            target=self.btn_split,
            view=self.view,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=-1,
            parent=self
        )
        self.view.accept_status.connect(self._on_split_dataset)

    @Slot(bool, list)
    def _on_split_dataset(self, accepted, _split_nums):
        if accepted:
            self._split_dataset()
            self._split_nums = _split_nums
        self.popup_tip.close()

    def _split_dataset(self):
        pass


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
        # self.btn_import.clicked.connect(self._on_import_clicked)l
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


class DatasetDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vly = QVBoxLayout(self)
        self.header = DatasetHeaderWidget()
        self.content = ClassifyDataset()
        self.vly.addWidget(self.header)
        self.vly.addWidget(self.content)
        self.vly.addStretch(1)
        self._dataset_info: DatasetInfo | None = None
        self._is_split = False

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self.header.set_header_info(dataset_info)
        self._dataset_info = dataset_info
