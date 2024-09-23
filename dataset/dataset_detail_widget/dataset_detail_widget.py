from PySide6.QtWidgets import QWidget, QVBoxLayout

from common.model_type_widget import ModelType
from .classify.classify_dataset_detail_widget import ClassifyDatasetDetailWidget
from .detection.detection_dataset_detail_widget import DetectionDatasetDetailWidget
from dataset.dataset_detail_widget.common.datset_header_widget import DatasetHeaderWidget
from dataset.dataset_list_widget.new_dataset_dialog import DatasetInfo
from .common.dataset_detail_widget_base import DatasetDetailWidgetBase
from loguru import logger


class DatasetDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vly = QVBoxLayout(self)
        self.header = DatasetHeaderWidget()
        self.content: DatasetDetailWidgetBase | None = None
        self.vly.addWidget(self.header)
        self._dataset_info: DatasetInfo | None = None
        self._is_split: bool = False

    def set_dataset_info(self, dataset_info: DatasetInfo):
        """
        设置数据集信息并更新UI组件。

        该方法首先将数据集信息设置到头部组件中，然后根据当前数据集的内容类型（分类或检测）
        更新详细信息面板。如果已经存在内容，它会删除当前的内容组件，并根据新的数据集类型
        创建并添加一个新的内容组件。

        参数:
        - dataset_info: DatasetInfo实例，包含数据集的相关信息。

        返回:
        无返回值。
        """
        # 将数据集信息设置到头部组件
        self.header.set_header_info(dataset_info)
        # 保存数据集信息到私有变量
        self._dataset_info = dataset_info

        # 如果当前有内容组件，删除并释放资源
        if self.content:
            try:
                # 断开信号与槽连接
                # self.content.load_dataset_finished.disconnect(self.header.set_dataset_header)
                self.header.split_dataset_clicked.disconnect(self.content.split_dataset)
            except TypeError:
                pass  # 可能尚未建立连接
            self.vly.removeWidget(self.content)
            self.content.deleteLater()
            self.content = None

        # 根据数据集的模型类型创建新的内容组件
        if self._dataset_info.model_type == ModelType.CLASSIFY:
            self.content = ClassifyDatasetDetailWidget()
        elif self._dataset_info.model_type == ModelType.DETECT:
            self.content = DetectionDatasetDetailWidget()
        else:
            # 如果模型类型不是分类或检测，记录日志并返回
            logger.warning(f"Unsupported model type: {self._dataset_info.model_type.name}")
            return

        # 将新的内容组件添加到布局中
        self.vly.addWidget(self.content)
        # 将数据集信息设置到内容组件中
        self.content.set_dataset_info(dataset_info)
        self.header.set_dataset_header(*self.content.get_dataset_split())
        # 连接内容组件和头部组件的信号和槽
        if self.content and self.header:
            # self.content.load_dataset_finished.connect(self.header.set_dataset_header)
            self.header.split_dataset_clicked.connect(self.content.split_dataset)
