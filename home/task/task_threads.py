from typing import Optional

from .model_trainer_thread.model_trainer_thread import ModelTrainThread


class TaskThreadMap:
    def __init__(self):
        self._max_map_len = 5
        self._thread_map: dict[str, ModelTrainThread] = dict()

    def update_thread(self, thread_map: dict[str, ModelTrainThread]):
        self._thread_map.update(thread_map)

    def get_thread_map(self) -> dict[str, ModelTrainThread]:
        return self._thread_map

    def get_thread_by_task_id(self, task_id) -> Optional[ModelTrainThread]:
        return self._thread_map.get(task_id, None)
