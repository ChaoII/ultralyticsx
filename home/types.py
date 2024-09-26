from enum import Enum
from pathlib import Path

from common.model_type_widget import ModelType
from common.utils import CustomColor


class TaskStatus(Enum):
    INITIALIZING = 0
    # dataset selected
    DS_SELECTED = 1
    # config finished
    CFG_FINISHED = 2
    # training
    TRAINING = 3
    TRN_FAILED = 4
    TRN_PAUSE = 5
    TRN_FINISHED = 6
    VAL_FINISHED = 7

    @property
    def color(self):
        _color_map = {
            TaskStatus.INITIALIZING: CustomColor.BLUE.value,
            TaskStatus.DS_SELECTED: CustomColor.BROWN.value,
            TaskStatus.CFG_FINISHED: CustomColor.YELLOW.value,
            TaskStatus.TRAINING: CustomColor.GRAY.value,
            TaskStatus.TRN_FAILED: CustomColor.PURPLE.value,
            TaskStatus.TRN_PAUSE: CustomColor.RED.value,
            TaskStatus.TRN_FINISHED: CustomColor.GREEN.value,
            TaskStatus.VAL_FINISHED: CustomColor.CYAN1.value,
        }
        return _color_map[self]


class ProjectInfo:
    project_name: str
    project_id: str
    project_description: str
    model_type: ModelType = ModelType.CLASSIFY
    project_dir: str
    create_time: str


class TaskInfo:
    task_id: str
    project_id: str
    dataset_id: str
    model_type: ModelType
    task_status: TaskStatus
    task_dir: Path
    create_time: str
