from typing import Optional

from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QTableWidget, \
    QSizePolicy, QHeaderView, QAbstractItemView
from qfluentwidgets import BodyLabel, ComboBox, CompactSpinBox, SwitchButton, \
    PrimaryPushButton, StateToolTip, TableWidget, \
    InfoBar, InfoBarPosition, ToolTipFilter, ToolTipPosition, CompactDoubleSpinBox, PushButton, FluentIcon

from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_icon import CustomFluentIcon
from ..model_trainer_thread.model_val_thread import ModelValThread
from ...types import TaskInfo


class FixWidthBodyLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(100)
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))


class ModelValWidget(CollapsibleWidgetItem):
    val_model_finished = Signal(bool)
    next_step_clicked = Signal(TaskInfo)

    def __init__(self, parent=None):
        super().__init__(self.tr("▌Model validation"), parent=parent)

        self.cmb_model_name = ComboBox()
        self.cmb_model_name.setFixedWidth(300)

        self.cmb_split = ComboBox()
        self.cmb_split.setFixedWidth(300)
        self.cmb_split.addItems(["train", "val", "test"])
        self.cmb_split.setCurrentIndex(2)

        self.btn_save_json = SwitchButton()
        self.btn_save_json.setChecked(False)
        self.btn_save_json.setFixedHeight(33)

        self.btn_save_hybrid = SwitchButton()
        self.btn_save_hybrid.setChecked(False)
        self.btn_save_hybrid.setFixedHeight(33)

        self.spb_conf = CompactDoubleSpinBox()
        self.spb_conf.setRange(0, 1)
        self.spb_conf.setValue(0.25)
        self.spb_conf.setFixedWidth(300)

        self.spb_iou = CompactDoubleSpinBox()
        self.spb_iou.setRange(0, 1)
        self.spb_iou.setValue(0.7)
        self.spb_iou.setFixedWidth(300)

        self.spb_max_det = CompactSpinBox()
        self.spb_max_det.setRange(1, 500)
        self.spb_max_det.setValue(300)
        self.spb_max_det.setFixedWidth(300)

        self.btn_half = SwitchButton()
        self.btn_half.setChecked(False)
        self.btn_half.setFixedHeight(33)

        self.btn_dnn = SwitchButton()
        self.btn_dnn.setChecked(False)
        self.btn_dnn.setFixedHeight(33)

        self.btn_plots = SwitchButton()
        self.btn_plots.setChecked(False)
        self.btn_plots.setFixedHeight(33)

        self.fly_train_setting1 = QFormLayout()
        self.fly_train_setting1.setVerticalSpacing(15)
        self.fly_train_setting1.setHorizontalSpacing(40)
        self.fly_train_setting1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_train_setting2 = QFormLayout()
        self.fly_train_setting2.setVerticalSpacing(15)
        self.fly_train_setting2.setHorizontalSpacing(40)
        self.fly_train_setting2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("model name: "), self), self.cmb_model_name)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("split: "), self), self.cmb_split)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("save_json: "), self), self.btn_save_json)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("btn_save_hybrid: "), self), self.btn_save_hybrid)
        self.fly_train_setting1.addRow(FixWidthBodyLabel(self.tr("conf: "), self), self.spb_conf)

        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("iou: "), self), self.spb_iou)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("max_det: "), self), self.spb_max_det)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("half: "), self), self.btn_half)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("dnn: "), self), self.btn_dnn)
        self.fly_train_setting2.addRow(FixWidthBodyLabel(self.tr("plots: "), self), self.btn_plots)

        self.vly_export_setting = QVBoxLayout()
        self.vly_export_setting.setSpacing(15)
        self.vly_export_setting.setContentsMargins(20, 0, 20, 0)

        self.hly_train_setting = QHBoxLayout()
        self.hly_train_setting.setSpacing(40)
        self.hly_train_setting.addLayout(self.fly_train_setting1)
        self.hly_train_setting.addLayout(self.fly_train_setting2)

        self.vly_export_setting.addLayout(self.hly_train_setting)

        self.hly_tb = QHBoxLayout()
        self.tb_val_result = TableWidget()
        self.tb_val_result.setAutoScroll(False)
        self.tb_val_result.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tb_val_result.setVisible(False)
        self.tb_val_result.verticalHeader().hide()
        self.tb_val_result.setBorderRadius(8)
        self.tb_val_result.setBorderVisible(True)
        self.hly_tb.addWidget(self.tb_val_result)
        self.hly_tb.addStretch(1)

        self.content_widget = QWidget(self)
        self.layout().addWidget(self.content_widget)

        self.vly_content = QVBoxLayout(self.content_widget)
        self.vly_content.setContentsMargins(20, 0, 20, 20)
        self.vly_content.setSpacing(30)

        self.vly_content.addLayout(self.vly_export_setting)
        self.hly_train_setting.addStretch(1)

        self.btn_val = PrimaryPushButton(CustomFluentIcon.MODEL_EXPORT, self.tr("Val"))
        self.btn_val.setFixedWidth(120)

        self.btn_next_step = PushButton(FluentIcon.RINGER, self.tr("Next step"))
        self.btn_next_step.setVisible(False)
        self.btn_next_step.setFixedWidth(120)

        self.hly_btn = QHBoxLayout()
        self.hly_btn.addWidget(self.btn_val)
        self.hly_btn.addWidget(self.btn_next_step)
        self.hly_btn.addStretch(1)

        self.vly_content.addLayout(self.hly_btn)
        self.vly_content.addLayout(self.hly_tb)

        self.set_content_widget(self.content_widget)
        self._task_info: TaskInfo | None = None
        self._export_parameter = dict()
        self._state_tool_tip = None
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.btn_val.clicked.connect(self._on_val_clicked)
        self.btn_next_step.clicked.connect(self._on_next_step_clicked)

    def set_task_info(self, task_info: TaskInfo):
        self._task_info = task_info
        self._init_model_name()
        self.tb_val_result.setVisible(False)
        self.tb_val_result.clear()
        self.btn_next_step.setVisible(False)

    def _init_model_name(self):
        self.cmb_model_name.clear()
        model_weight_path = self._task_info.task_dir / "weights"
        if not model_weight_path.exists():
            return
        for item in model_weight_path.iterdir():
            if item.is_file() and item.suffix == ".pt":
                self.cmb_model_name.addItem(item.name)
        self.cmb_model_name.setCurrentIndex(0)

    def create_val_thread(self) -> Optional[ModelValThread]:
        model_export_thread = ModelValThread(self._export_parameter)
        model_export_thread.model_val_start.connect(self._on_val_start)
        model_export_thread.model_val_end.connect(self._on_val_end)
        model_export_thread.model_val_batch_end.connect(self._on_val_batch_end)
        model_export_thread.model_val_failed.connect(self._on_val_failed)

        if model_export_thread.init_model_exporter():
            return model_export_thread
        else:
            return None

    def _on_next_step_clicked(self):
        self.next_step_clicked.emit(self._task_info)

    def _on_val_start(self, epoch):
        self.val_model_finished.emit(False)
        self.btn_val.setEnabled(False)
        self.btn_next_step.setVisible(False)

    def _on_val_batch_end(self, epoch):
        # print(epoch, epochs)
        pass

    def _on_val_end(self, val_results: list):
        self.state_tool_tip.setContent(
            self.tr('Export Model completed!') + ' 😆')
        self.state_tool_tip.setState(True)
        self.state_tool_tip = None
        self.val_model_finished.emit(True)
        self.btn_val.setEnabled(True)
        self.btn_next_step.setVisible(True)

        self.tb_val_result.clear()
        self.tb_val_result.setVisible(True)

        self.tb_val_result.setRowCount(len(val_results[1:]))
        self.tb_val_result.setColumnCount(len(val_results[0]))
        self.tb_val_result.setHorizontalHeaderLabels(val_results[0])
        self.setMinimumHeight(38 * len(val_results))

        for row, results in enumerate(val_results[1:]):
            for col, result in enumerate(results):
                if col == 0:
                    item = QTableWidgetItem(result)
                else:
                    item = QTableWidgetItem(f"{result:.4f}")
                self.tb_val_result.setItem(row, col, item)
        self.tb_val_result.resizeColumnsToContents()
        min_height = 0
        min_width = 0
        for row in range(self.tb_val_result.rowCount()):
            min_height += self.tb_val_result.rowHeight(row)

        for col in range(self.tb_val_result.columnCount()):
            min_width += self.tb_val_result.columnWidth(col)

        self.setMinimumSize(min_width, min_height)
        self.update()
        print(min_width, min_height)

        print(self.tb_val_result.rowHeight(0))

    @Slot(str)
    def _on_val_failed(self, error_msg: str):
        if self._state_tool_tip:
            self.state_tool_tip.setState(True)
            self.state_tool_tip = None
            self.val_model_finished.emit(True)
            self.btn_val.setEnabled(True)
            InfoBar.error(
                title='',
                content=self.tr("val model failed: ") + error_msg,
                orient=Qt.Orientation.Vertical,  # 内容太长时可使用垂直布局
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self.parent().parent()
            )

    def val(self):
        task_thread = self.create_val_thread()
        task_thread.start()

    def _on_val_clicked(self):
        parameter = dict(
            model_name=self._task_info.task_dir / "weights" / self.cmb_model_name.currentText(),
            split=self.cmb_split.currentText(),
            save_json=self.btn_save_json.isChecked(),
            save_hybrid=self.btn_save_hybrid.isChecked(),
            conf=self.spb_conf.value(),
            iou=self.spb_iou.value(),
            max_det=self.spb_max_det.value(),
            half=self.btn_half.isChecked(),
            dnn=self.btn_dnn.isChecked(),
            plots=self.btn_plots.isChecked()
        )
        self._export_parameter = parameter
        self.val()
        self.state_tool_tip = StateToolTip(
            self.tr('Model is exporting '), self.tr('Please wait patiently'), self.window())
        self.state_tool_tip.move(self.state_tool_tip.getSuitablePos())
        self.state_tool_tip.show()
