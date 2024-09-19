from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import BodyLabel, TextWrap, ImageLabel
from common.collapsible_widget import CollapsibleWidgetItem
from common.custom_scroll_widget import CustomScrollWidget
from common.model_type_widget import ModelType


class ClassifyDocWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        vly = QVBoxLayout(self)
        self.lbl_content = BodyLabel(self)
        self.lbl_content.setWordWrap(True)
        self.lbl_image = ImageLabel()
        vly.addWidget(self.lbl_content)
        vly.addWidget(self.lbl_image)

        self._init_widgets()

    def _init_widgets(self):
        self.lbl_content.setText(
            "1.需要选定数据集所在文件夹路径(路径中仅含一个数据集)\n"
            "2.不支持.zip、tar.gz等压缩包形式的数据\n"
            "3.导入图片格式支持png，jpg，jpeg，bmp格式\n"
            "4.文件夹名为需要分类的类名，输入限定为英文字符，不可包含空格、中文或特殊字符")
        self.lbl_image.setImage("resource/images/classify_help.png")
        self.lbl_image.scaledToWidth(450)


class DetectionDocWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        vly = QVBoxLayout(self)
        self.lbl_content = BodyLabel(self)
        self.lbl_content.setWordWrap(True)
        self.lbl_image = ImageLabel()
        vly.addWidget(self.lbl_content)
        vly.addWidget(self.lbl_image)
        self._init_widgets()

    def _init_widgets(self):
        self.lbl_content.setText(
            "1.需要选定数据集所在文件夹路径(路径中仅含一个数据集)\n"
            "2.不支持.zip、tar.gz等压缩包形式的数据\n"
            "3.导入图片格式支持png，jpg，jpeg，bmp格式\n"
            "4.文件夹名为需要分类的类名，输入限定为英文字符，不可包含空格、中文或特殊字符")
        self.lbl_image.setImage("resource/images/classify_help.png")
        self.lbl_image.scaledToWidth(450)


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
        self.classify_doc = CollapsibleWidgetItem(self.tr("▌Classify"))
        self.classify_doc.set_content_widget(ClassifyDocWidget())

        self.detection_doc = CollapsibleWidgetItem(self.tr("▌Detection"))
        self.detection_doc.set_content_widget(DetectionDocWidget())

        self.segmentation_doc = CollapsibleWidgetItem(self.tr("▌Segmentation"))
        self.OBB_doc = CollapsibleWidgetItem(self.tr("▌OBB"))
        self.pose_doc = CollapsibleWidgetItem(self.tr("▌Pose"))
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

        self.setFixedWidth(500)
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.classify_doc.collapse_clicked.connect(lambda: self.set_current_model_type(ModelType.CLASSIFY))
        self.detection_doc.collapse_clicked.connect(lambda: self.set_current_model_type(ModelType.DETECTION))
        self.segmentation_doc.collapse_clicked.connect(lambda: self.set_current_model_type(ModelType.SEGMENT))
        self.OBB_doc.collapse_clicked.connect(lambda: self.set_current_model_type(ModelType.OBB))
        self.pose_doc.collapse_clicked.connect(lambda: self.set_current_model_type(ModelType.POSE))

    def _collapse_all_doc(self):
        self.classify_doc.set_collapsed(True)
        self.detection_doc.set_collapsed(True)
        self.segmentation_doc.set_collapsed(True)
        self.OBB_doc.set_collapsed(True)
        self.pose_doc.set_collapsed(True)

    def set_current_model_type(self, model_type: ModelType):
        self._collapse_all_doc()
        if model_type == ModelType.CLASSIFY:
            self.classify_doc.set_collapsed(False)
        if model_type == ModelType.DETECTION:
            self.detection_doc.set_collapsed(False)
        if model_type == ModelType.SEGMENT:
            self.segmentation_doc.set_collapsed(False)
        if model_type == ModelType.OBB:
            self.OBB_doc.set_collapsed(False)
        if model_type == ModelType.POSE:
            self.pose_doc.set_collapsed(False)
