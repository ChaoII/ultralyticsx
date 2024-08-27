import json
from pathlib import Path
from pprint import pprint

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import SimpleCardWidget, SubtitleLabel, BodyLabel, HyperlinkLabel, PopupTeachingTip, \
    TeachingTipTailPosition

from dataset.dataset_detail_widget.dataset_split_view import DatasetSplitFlyoutView
from dataset.types import DatasetInfo


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

        self._total_dataset = 0
        self._dataset_map = dict()
        self._split_rates = []
        self._dataset_info: DatasetInfo | None = None
        self._connect_signals_and_slots()

    def set_dataset_info(self, dataset_info: DatasetInfo):
        self._dataset_info = dataset_info
        self.dataset_analysis()

    def dataset_analysis(self):
        self._dataset_map.clear()
        self._total_dataset = 0
        for item in Path(self._dataset_info.dataset_dir).iterdir():
            if item.is_dir():
                images = list(map(lambda x: x.resolve().as_posix(), item.iterdir()))
                self._dataset_map[item.name] = images
                self._total_dataset += len(images)

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
            self._split_dataset()
            self._split_rates = split_rates
        self.popup_tip.close()

    def _split_dataset(self):
        pprint(self._dataset_map)
