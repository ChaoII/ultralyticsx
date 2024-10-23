from enum import Enum

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
