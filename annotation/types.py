from enum import Enum

from common.component.model_type_widget import ModelType
from common.utils.utils import CustomColor


class AnnotationStatus(Enum):
    Initialing = 0
    Annotating = 1
    AnnoFinished = 2

    @property
    def color(self):
        _color_map = {
            AnnotationStatus.Initialing: CustomColor.ORANGE.value,
            AnnotationStatus.Annotating: CustomColor.GREEN.value,
            AnnotationStatus.AnnoFinished: CustomColor.RED.value,
        }

        return _color_map[self]


class AnnotationTaskInfo:
    annotation_task_name: str
    annotation_task_id: str
    annotation_task_description: str
    annotation_task_status: AnnotationStatus
    model_type: ModelType
    image_dir: str
    annotation_dir: str
