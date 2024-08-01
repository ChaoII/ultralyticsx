from qfluentwidgets import HeaderCardWidget, BodyLabel, ComboBox, CheckBox
from PySide6.QtWidgets import QFormLayout, QHBoxLayout
from PySide6.QtCore import Slot, Signal, Qt
from .options import *


class ModelInfoCard(HeaderCardWidget):
    """ Model information card """
    # model name and is use pretrain model
    model_status_changed = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("select model"))

        # model type
        self.model_type_label = BodyLabel(self.tr('model type: '), self)
        self.model_type_cmb = ComboBox()
        self.model_type_cmb.addItems(model_type_option)
        self.model_type_cmb.setPlaceholderText(self.tr("select a model type"))
        self.model_type_cmb.setCurrentIndex(-1)
        self.model_type_cmb.setMinimumWidth(200)
        self.model_type_cmb.setMaximumWidth(600)
        # model name
        self.model_name_label = BodyLabel(self.tr('model name: '), self)
        self.model_name_cmb = ComboBox()
        self.model_name_cmb.setMinimumWidth(200)
        self.model_name_cmb.setMaximumWidth(600)
        # use pretrain model
        self.use_pretrain_model_cb = CheckBox()
        self.use_pretrain_model_cb.setText(self.tr("user pretrain model"))
        self.use_pretrain_model_cb.setChecked(True)

        self.model_type_fly = QFormLayout()
        self.model_name_fly = QFormLayout()

        self.model_type_fly.addRow(self.model_type_label, self.model_type_cmb)
        self.model_name_fly.addRow(self.model_name_label, self.model_name_cmb)

        self.hly = QHBoxLayout()
        self.hly.setSpacing(10)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.hly.addLayout(self.model_type_fly)
        self.hly.addLayout(self.model_name_fly)
        self.hly.addWidget(self.use_pretrain_model_cb)
        self.viewLayout.addLayout(self.hly)

        self._connect_signals_and_slots()

        self.use_pretrain_model = True
        self.cur_model_name = ""

    def _connect_signals_and_slots(self):
        self.model_type_cmb.currentTextChanged.connect(self._on_model_type_changed)
        self.model_name_cmb.currentTextChanged.connect(self._on_model_name_changed)
        self.use_pretrain_model_cb.checkStateChanged.connect(self._on_use_pretrain_model_status_changed)

    @Slot(str)
    def _on_model_type_changed(self, model_type: str):
        model_names = type_model_mapping.get(model_type, [])
        self.model_name_cmb.clear()
        for model_name in model_names:
            self.model_name_cmb.addItem(model_name)

    @Slot(str)
    def _on_model_name_changed(self, model_name: str):
        self.cur_model_name = model_name
        self.model_status_changed.emit(self.cur_model_name, self.use_pretrain_model)

    @Slot(Qt.CheckState)
    def _on_use_pretrain_model_status_changed(self, status: Qt.CheckState):
        self.use_pretrain_model = status == Qt.CheckState.Checked
        self.model_status_changed.emit(self.cur_model_name, self.use_pretrain_model)
