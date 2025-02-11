from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import BreadcrumbBar

from annotation.annotation_task_list_widget import AnnotationTaskListWidget
from annotation.annotation_widget import AnnotationWidget
from common.core.content_widget_base import ContentWidgetBase
from common.core.interface_base import InterfaceBase


class AnnotationInterface(InterfaceBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("annotation_interface")
        self.vly = QVBoxLayout(self)
        self.vly.setSpacing(9)
        self.breadcrumbBar = BreadcrumbBar(self)
        self.stackedWidget = QStackedWidget(self)
        self.annotation_task_list_widget = AnnotationTaskListWidget()
        self.annotation_widget = AnnotationWidget(self)
        self.stackedWidget.addWidget(self.annotation_task_list_widget)
        self.stackedWidget.addWidget(self.annotation_widget)
        self.breadcrumbBar.addItem(self.annotation_task_list_widget.objectName(), self.tr("All annotation task"))
        self.vly.addWidget(self.breadcrumbBar)
        self.vly.addWidget(self.stackedWidget)
        self._on_connect_signals_and_slots()

    def _on_connect_signals_and_slots(self):
        self.breadcrumbBar.currentItemChanged.connect(self._on_bread_bar_item_changed)
        self.annotation_task_list_widget.start_annotation_clicked.connect(self._on_start_annotation_clicked)

    #     self.dataset_list_widget.import_dataset_clicked.connect(self._on_import_dataset_clicked)
    #     self.dataset_list_widget.view_dataset_clicked.connect(self._on_view_dataset_clicked)
    #     self.import_dataset_widget.check_and_import_finished.connect(self._on_imported_finished)
    #
    # @Slot(DatasetInfo)
    # def _on_import_dataset_clicked(self, dataset_info: DatasetInfo):
    #     self.import_dataset_widget.set_dataset_info(dataset_info)
    #     self.stackedWidget.setCurrentWidget(self.import_dataset_widget)
    #     self.breadcrumbBar.addItem(self.import_dataset_widget.objectName(), dataset_info.dataset_name)
    #
    # def _on_imported_finished(self, dataset_info: DatasetInfo):
    #     self.breadcrumbBar.popItem()
    #     self.stackedWidget.setCurrentWidget(self.dataset_detail_widget)
    #     self.dataset_detail_widget.set_dataset_info(dataset_info)
    #     self.breadcrumbBar.addItem(self.dataset_detail_widget.objectName(), dataset_info.dataset_name)
    #
    @Slot(str)
    def _on_start_annotation_clicked(self, annotation_task_id: str):
        self.stackedWidget.setCurrentWidget(self.annotation_widget)
        self.annotation_widget.set_annotation_task_id(annotation_task_id)
        self.breadcrumbBar.addItem(self.annotation_widget.objectName(), annotation_task_id)

    # @Slot()
    # def _on_create_task_clicked(self):
    #     self.stackedWidget.setCurrentWidget(self.dataset_detail_widget)
    #     self.breadcrumbBar.addItem(self.dataset_detail_widget.objectName(), self.tr("Create dataset"))

    def update_widget(self):
        self.breadcrumbBar.setCurrentItem(self.annotation_task_list_widget.objectName())

    @Slot(str)
    def _on_bread_bar_item_changed(self, obj_name):
        obj = self.findChild(QWidget, obj_name)
        if isinstance(obj, ContentWidgetBase):
            self.stackedWidget.setCurrentWidget(obj)
            obj.update_widget()
