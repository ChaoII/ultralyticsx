from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import BreadcrumbBar

from .dataset_detail_widget import DatasetDetailWidget
from .dataset_list_widget import DatasetListWidget
from .import_dataset_widget import ImportDatasetWidget
from .new_dataset_dialog import DatasetInfo


class DatasetWidget(QWidget):
    def __init__(self, parent=None):
        super(DatasetWidget, self).__init__(parent=parent)
        self.setObjectName("dataset_widget")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.breadcrumbBar = BreadcrumbBar(self)
        self.stackedWidget = QStackedWidget(self)
        self.dataset_list_widget = DatasetListWidget()
        self.import_dataset_widget = ImportDatasetWidget()
        self.dataset_detail_widget = DatasetDetailWidget()

        self.stackedWidget.addWidget(self.dataset_list_widget)
        self.stackedWidget.addWidget(self.import_dataset_widget)
        self.stackedWidget.addWidget(self.dataset_detail_widget)

        self.breadcrumbBar.addItem(self.dataset_list_widget.objectName(), self.tr("All dataset"))

        self.vly.addWidget(self.breadcrumbBar)
        self.vly.addWidget(self.stackedWidget)
        self._on_connect_signals_and_slots()

    def _on_connect_signals_and_slots(self):
        self.breadcrumbBar.currentItemChanged.connect(self._on_bread_bar_item_changed)
        self.dataset_list_widget.import_dataset_clicked.connect(self._on_import_dataset_clicked)
        self.dataset_list_widget.view_dataset_clicked.connect(self._on_view_dataset_clicked)
        # self.dataset_list_widget.
        # self.dataset_list_widget.create_dataset_clicked.connect(self._on_create_task_clicked)

    @Slot(DatasetInfo)
    def _on_import_dataset_clicked(self, dataset_info: DatasetInfo):
        self.stackedWidget.setCurrentWidget(self.import_dataset_widget)
        self.import_dataset_widget.set_dataset_info(dataset_info)
        self.breadcrumbBar.addItem(self.import_dataset_widget.objectName(), dataset_info.dataset_name)

    @Slot(DatasetInfo)
    def _on_view_dataset_clicked(self, dataset_info: DatasetInfo):
        self.stackedWidget.setCurrentWidget(self.dataset_detail_widget)
        self.dataset_detail_widget.set_dataset_info(dataset_info)
        self.breadcrumbBar.addItem(self.dataset_detail_widget.objectName(), dataset_info.dataset_name)

    # @Slot()
    # def _on_create_task_clicked(self):
    #     self.stackedWidget.setCurrentWidget(self.dataset_detail_widget)
    #     self.breadcrumbBar.addItem(self.dataset_detail_widget.objectName(), self.tr("Create dataset"))

    @Slot(str)
    def _on_bread_bar_item_changed(self, obj_name):
        obj = self.findChild(QWidget, obj_name)
        if isinstance(obj, QWidget):
            self.stackedWidget.setCurrentWidget(obj)
