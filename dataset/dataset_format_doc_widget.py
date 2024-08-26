from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import BodyLabel
from common.collapsible_widget import CollapsibleWidget
from common.cust_scrollwidget import CustomScrollWidget
from common.model_type_widget import ModelType


class ClassifyDocWidget(QWidget):
    def __init__(self, cc, parent=None):
        super().__init__(parent=parent)
        vly = QVBoxLayout(self)
        self.til = BodyLabel(cc, self)
        vly.addWidget(self.til)


class DetectionDocWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class SegmentationDocWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class OBBDocWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class PoseDocWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class DatasetFormatDocWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.classify_doc = CollapsibleWidget(self.tr("Classify"))
        self.classify_doc.set_content_widget(ClassifyDocWidget("1231"))
        self.classify_doc.set_content_widget(ClassifyDocWidget("35434"))

        self.detection_doc = CollapsibleWidget(self.tr("Detection"))
        self.segmentation_doc = CollapsibleWidget(self.tr("Segmentation"))
        self.OBB_doc = CollapsibleWidget(self.tr("OBB"))
        self.pose_doc = CollapsibleWidget(self.tr("Pose"))
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.setSpacing(0)

        self.vly_dataset_info.addWidget(self.classify_doc)
        self.vly_dataset_info.addWidget(self.detection_doc)
        self.vly_dataset_info.addWidget(self.segmentation_doc)
        self.vly_dataset_info.addWidget(self.OBB_doc)
        self.vly_dataset_info.addWidget(self.pose_doc)
        self.vly_dataset_info.addStretch(1)
        self.scroll_area = CustomScrollWidget(orient=Qt.Orientation.Vertical)
        self.scroll_area.setLayout(self.vly_dataset_info)

        self.vly_content = QVBoxLayout(self)
        self.vly_content.addWidget(self.scroll_area)

    def _collapse_all_doc(self):
        self.classify_doc.set_content_hidden(True)
        self.detection_doc.set_content_hidden(True)
        self.segmentation_doc.set_content_hidden(True)
        self.OBB_doc.set_content_hidden(True)
        self.pose_doc.set_content_hidden(True)

    def set_current_model_type(self, model_type: ModelType):
        self._collapse_all_doc()
        if model_type == ModelType.CLASSIFY:
            self.classify_doc.set_content_hidden(False)
        if model_type == ModelType.DETECT:
            self.detection_doc.set_content_hidden(False)
        if model_type == ModelType.SEGMENT:
            self.segmentation_doc.set_content_hidden(False)
        if model_type == ModelType.OBB:
            self.OBB_doc.set_content_hidden(False)
        if model_type == ModelType.POSE:
            self.pose_doc.set_content_hidden(False)
