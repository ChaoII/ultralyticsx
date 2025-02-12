from PySide6.QtWidgets import QWidget, QVBoxLayout
from loguru import logger

from common.component.model_type_widget import ModelType
from common.utils.raise_info_bar import raise_error
from .classify.classify_dataset_detail_widget import ClassifyDatasetDetailWidget
from .common.dataset_detail_widget_base import DatasetDetailWidgetBase
from .common.datset_header_widget import DatasetHeaderWidget
from .detection.detection_dataset_detail_widget import DetectionDatasetDetailWidget
from .obb.obb_dataset_detail_widget import OBBDatasetDetailWidget
from .pose.pose_dataset_detail_widget import PoseDatasetDetailWidget
from .segment.segment_dataset_detail_widget import SegmentDatasetDetailWidget
from ..dataset_list_widget.new_dataset_dialog import DatasetInfo


class DatasetDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vly = QVBoxLayout(self)
        self.header = DatasetHeaderWidget()
        self.content: DatasetDetailWidgetBase | None = None
        self.vly.addWidget(self.header)
        self._dataset_info: DatasetInfo | None = None
        self._is_split: bool = False
        self._is_connected: bool = False

    def set_dataset_info(self, dataset_info: DatasetInfo) -> bool:
        # 将数据集信息设置到头部组件
        self.header.set_header_info(dataset_info)
        # 保存数据集信息到私有变量
        self._dataset_info = dataset_info
        # 如果当前有内容组件，删除并释放资源
        if self.content:
            if self._is_connected:
                # self.content.load_dataset_finished.disconnect(self.header.set_dataset_header)
                self.header.split_dataset_clicked.disconnect(self.content.split_dataset)
                self._is_connected = False
            self.vly.removeWidget(self.content)
            self.content.deleteLater()
            self.content = None

        # 根据数据集的模型类型创建新的内容组件
        if self._dataset_info.model_type == ModelType.CLASSIFY:
            self.content = ClassifyDatasetDetailWidget()
        elif self._dataset_info.model_type == ModelType.DETECT:
            self.content = DetectionDatasetDetailWidget()
        elif self._dataset_info.model_type == ModelType.SEGMENT:
            self.content = SegmentDatasetDetailWidget()
        elif self._dataset_info.model_type == ModelType.POSE:
            self.content = PoseDatasetDetailWidget()
        elif self._dataset_info.model_type == ModelType.OBB:
            self.content = OBBDatasetDetailWidget()
        else:
            # 如果模型类型不是分类或检测，记录日志并返回
            logger.error(f"Unsupported model type: {self._dataset_info.model_type.name}")
            raise raise_error(self.tr("Unsupported model type"))

        # 将新的内容组件添加到布局中
        self.vly.addWidget(self.content)
        # 将数据集信息设置到内容组件中
        if not self.content.set_dataset_info(dataset_info):
            return False
        self.header.set_dataset_header(*self.content.get_dataset_split())
        # 连接内容组件和头部组件的信号和槽
        if self.content and self.header:
            # self.content.load_dataset_finished.connect(self.header.set_dataset_header)
            self.header.split_dataset_clicked.connect(self.content.split_dataset)
            self._is_connected = True
        return True
