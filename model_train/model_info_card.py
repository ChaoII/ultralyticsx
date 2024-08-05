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
        self.lbl_model_type = BodyLabel(self.tr('model type: '), self)
        self.cmb_model_type = ComboBox()
        self.cmb_model_type.addItems(model_type_option)
        self.cmb_model_type.setPlaceholderText(self.tr("select a model type"))
        self.cmb_model_type.setCurrentIndex(-1)
        self.cmb_model_type.setMinimumWidth(200)
        self.cmb_model_type.setMaximumWidth(600)
        # model name
        self.lbl_model_name = BodyLabel(self.tr('model name: '), self)
        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setMinimumWidth(200)
        self.cmb_model_name.setMaximumWidth(600)
        # use pretrain model
        self.ckb_use_pretrain_model = CheckBox()
        self.ckb_use_pretrain_model.setText(self.tr("user pretrain model"))
        self.ckb_use_pretrain_model.setChecked(True)

        self.model_type_fly = QFormLayout()
        self.model_name_fly = QFormLayout()
        self.is_pretrain_fly = QFormLayout()

        self.model_type_fly.addRow(self.lbl_model_type, self.cmb_model_type)
        self.model_name_fly.addRow(self.lbl_model_name, self.cmb_model_name)
        self.is_pretrain_fly.addRow(BodyLabel(), self.ckb_use_pretrain_model)

        self.hly = QHBoxLayout()
        self.hly.setSpacing(10)
        self.hly.setContentsMargins(0, 0, 0, 0)
        self.hly.addLayout(self.model_type_fly)
        self.hly.addLayout(self.model_name_fly)
        self.hly.addLayout(self.is_pretrain_fly)
        # self.hly.addWidget(self.ckb_use_pretrain_model)
        self.viewLayout.addLayout(self.hly)

        self._connect_signals_and_slots()

        self.use_pretrain_model = True
        self.cur_model_name = ""

    def _connect_signals_and_slots(self):
        self.cmb_model_type.currentTextChanged.connect(self._on_model_type_changed)
        self.cmb_model_name.currentTextChanged.connect(self._on_model_name_changed)
        self.ckb_use_pretrain_model.checkStateChanged.connect(self._on_use_pretrain_model_status_changed)

    @Slot(str)
    def _on_model_type_changed(self, model_type: str):
        model_names = type_model_mapping.get(model_type, [])
        self.cmb_model_name.clear()
        for model_name in model_names:
            self.cmb_model_name.addItem(model_name)

    @Slot(str)
    def _on_model_name_changed(self, model_name: str):
        self.cur_model_name = model_name
        self.model_status_changed.emit(self.cur_model_name, self.use_pretrain_model)

    @Slot(Qt.CheckState)
    def _on_use_pretrain_model_status_changed(self, status: Qt.CheckState):
        self.use_pretrain_model = status == Qt.CheckState.Checked
        self.model_status_changed.emit(self.cur_model_name, self.use_pretrain_model)
