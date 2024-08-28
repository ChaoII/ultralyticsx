from PySide6.QtCore import Signal, Qt, QSize, Slot
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout
from qfluentwidgets import BodyLabel, CompactSpinBox, FlyoutViewBase, themeColor, PrimaryPushButton, PushButton, \
    InfoBarIcon, TransparentToolButton, StrongBodyLabel, InfoBarPosition, InfoBar
from qfluentwidgets import SubtitleLabel, HyperlinkLabel, PopupTeachingTip, TeachingTipTailPosition

from common.custom_label_widget import CustomLabel


class SplitDatasetContentWidget(QWidget):
    rate_changed = Signal(list)

    def __init__(self, total_dataset: int, rates: list):
        super().__init__()
        self._rates = rates
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
        self.csb_training_rate.setValue(self._rates[0])
        self.csb_training_rate.setRange(0, 100)

        self.csb_validation_rate = CompactSpinBox()
        self.csb_validation_rate.setValue(self._rates[1])
        self.csb_validation_rate.setRange(0, 100)

        self.csb_testing_rate = CompactSpinBox()
        self.csb_testing_rate.setValue(self._rates[2])
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
        self._rates[index] = value
        self.update_num()
        self.rate_changed.emit(self._rates)

    def update_num(self):
        self.lbl_training_num.setText(str(int(self.total_dataset * self._rates[0] / 100)))
        self.lbl_validation_num.setText(str(int(self.total_dataset * self._rates[1] / 100)))
        self.lbl_testing_num.setText(str(int(self.total_dataset * self._rates[2] / 100)))


class DatasetSplitFlyoutView(FlyoutViewBase):
    def addWidget(self, widget: QWidget, stretch=0, align=Qt.AlignmentFlag.AlignLeft):
        pass

    accept_status = Signal(bool, list)

    def __init__(self, total_datasets: int, parent=None):
        super().__init__(parent)
        self._split_rates = [70, 20, 10]
        self.setFixedWidth(440)
        self.vBoxLayout = QVBoxLayout(self)
        self.lbl_title = StrongBodyLabel(self.tr("Dataset split"), self)
        self.icon = TransparentToolButton(InfoBarIcon.WARNING, parent=self)
        self.icon.setIconSize(QSize(20, 20))
        self.lbl_tips = CustomLabel(self.tr("Tip: The sum of three datasets must be 100%, "
                                            "the test set can be 0, and the validation set cannot be 0"), self)
        self.lbl_tips.setWordWrap(True)
        self.lbl_tips.setTextColor(themeColor(), themeColor())

        self.btn_split = PrimaryPushButton(self.tr('Split'), self)
        self.btn_cancel = PushButton(self.tr("Cancel"), self)
        self.btn_split.setFixedWidth(120)
        self.btn_cancel.setFixedWidth(120)
        self.hly_content = QHBoxLayout()
        self.hly_content.addWidget(self.icon)
        self.hly_content.addWidget(self.lbl_tips)

        self.split_dataset_content_widget = SplitDatasetContentWidget(total_datasets, self._split_rates)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addStretch(1)
        self.hly_btn.addWidget(self.btn_split)
        self.hly_btn.addWidget(self.btn_cancel)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(self.lbl_title)
        self.vBoxLayout.addLayout(self.hly_content)
        self.vBoxLayout.addWidget(self.split_dataset_content_widget)
        self.vBoxLayout.addLayout(self.hly_btn)

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_split.clicked.connect(lambda: self._on_btn_clicked(True))
        self.btn_cancel.clicked.connect(lambda: self._on_btn_clicked(False))
        self.split_dataset_content_widget.rate_changed.emit(self._on_rate_changed)

    def _on_btn_clicked(self, status: bool):
        if status and sum(self._split_rates) != 100:
            InfoBar.error(
                title='',
                content=self.tr("Split dataset error!"),
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self.parent().parent()
            )
            return
        self.accept_status.emit(status, self._split_rates)

    @Slot(list)
    def _on_rate_changed(self, _split_rates: list):
        print(_split_rates)
        self._split_rates = _split_rates


class DatasetSplitWidget(QWidget):
    split_clicked = Signal(list)

    def __init__(self):
        super().__init__()
        self.lbl_title = SubtitleLabel("▌" + self.tr("Data analysis"), self)
        self.lbl_split_tip = BodyLabel(self.tr("Dataset have split, you can split again"), self)
        self.btn_split = HyperlinkLabel(self.tr("Split again"))
        self.btn_split.setUnderlineVisible(True)
        self.hly_dataset_info = QHBoxLayout(self)
        self.hly_dataset_info.setSpacing(30)
        self.hly_dataset_info.addWidget(self.lbl_title)
        self.hly_dataset_info.addWidget(self.lbl_split_tip)
        self.hly_dataset_info.addWidget(self.btn_split)
        self.hly_dataset_info.addStretch(1)

        self._total_dataset = 0
        self._connect_signals_and_slots()

    def set_total_dataset(self, total_dataset: int):
        self._total_dataset = total_dataset

    def _connect_signals_and_slots(self):
        self.btn_split.clicked.connect(self._on_split_clicked)

    def _on_split_clicked(self):
        self.view = DatasetSplitFlyoutView(self._total_dataset)
        self.popup_tip = PopupTeachingTip.make(
            target=self.btn_split,
            view=self.view,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=-1,
            parent=self
        )
        self.view.accept_status.connect(self._on_split_dataset)

    @Slot(bool, list)
    def _on_split_dataset(self, accepted, split_rates):
        if accepted:
            self._split_rates = split_rates
            self.split_clicked.emit(self._split_rates)
        self.popup_tip.close()
