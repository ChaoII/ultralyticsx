import pickle
from pathlib import Path
from typing import IO
from loguru import logger
from PySide6.QtCore import Slot, Signal, QThread, QObject

from common.utils import log_info, log_error
from home.types import TaskInfo, TaskStatus
from ultralytics.models.yolo.classify import ClassificationTrainer


class CustomLogs(QObject):
    log_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._logs = []

    def append(self, message: str):
        self._logs.append(message)
        self.log_changed.emit(message)

    def get_log_lines(self):
        return self._logs

    def save_to_file(self, file_path: Path, mode="w"):
        with open(file_path, mode=mode, encoding="utf8") as f:
            logs = "\n".join(self._logs)
            f.write(logs)

    def load_log_from_text(self, file_path: Path):
        with open(file_path, encoding="utf8") as f:
            self._logs = f.readlines()

    def clear(self):
        self._logs.clear()


class CustomPlotData(QObject):
    plot_data_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._plot_data: dict[str, list] = dict()

    def is_empty(self):
        return len(self._plot_data) == 0

    def raw_data(self) -> dict[str, list]:
        return self._plot_data

    def set_plot_data(self, plot_data: dict[str, list]):
        self._plot_data = plot_data
        self.plot_data_changed.emit(self._plot_data)

    def clear_data(self):
        self._plot_data = dict()

    def init_plot_data(self, init_data: list | dict):
        if isinstance(init_data, list):
            for loss_name in init_data:
                self._plot_data[loss_name] = []
        elif isinstance(init_data, dict):
            for key, value in init_data.items():
                self._plot_data[key] = []
        else:
            logger.error(f"unsupported type {type(init_data)}, only support list and dict")
            return
        # self.plot_data_changed.emit(self._plot_data)

    def append(self, data_dict: dict[str, float]):
        for key, value in data_dict.items():
            self._plot_data[key].append(data_dict[key])
        self.plot_data_changed.emit(self._plot_data)

    def save_to_file(self, file_path: Path, mode="wb"):
        with open(file_path, mode=mode) as f:
            pickle.dump(self._plot_data, f)

    def load_from_file(self, file_path: Path):
        with open(file_path, encoding="utf8") as f:
            self._plot_data = pickle.load(f)
        self.plot_data_changed.emit(self._plot_data)


class ModelTrainThread(QThread):
    train_start_signal = Signal(dict, dict)
    train_epoch_end = Signal(int)
    model_train_end = Signal(TaskInfo)
    model_train_failed = Signal(str)

    log_changed_signal = Signal(str)
    loss_changed_signal = Signal(dict)
    metric_changed_signal = Signal(dict)

    def __init__(self, train_parameters: dict):
        super(ModelTrainThread, self).__init__()
        self.trainer: ClassificationTrainer | None = None
        self._train_parameters = train_parameters
        self._stop = False
        self._metric_num = 0
        self._task_info: TaskInfo | None = None
        self._loss_data = CustomPlotData()
        self._metric_data = CustomPlotData()
        self._train_loss_path: Path | None = None
        self._train_metric_path: Path | None = None
        self._train_log_path: Path | None = None
        self._last_model = ""
        self._logs = CustomLogs()
        self._current_epoch = 0

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self._logs.log_changed.connect(lambda msg: self.log_changed_signal.emit(msg))
        self._loss_data.plot_data_changed.connect(lambda loss: self.loss_changed_signal.emit(loss))
        self._metric_data.plot_data_changed.connect(lambda metric: self.metric_changed_signal.emit(metric))

    def init_model_trainer(self, task_info: TaskInfo) -> bool:
        try:
            self.trainer = ClassificationTrainer(overrides=self._train_parameters)
            self.trainer.add_callback("on_train_start", self._on_train_start)
            self.trainer.add_callback("on_train_batch_start", self._on_train_batch_start)
            self.trainer.add_callback("on_train_batch_end", self._on_train_batch_end)
            self.trainer.add_callback("on_train_epoch_start", self._on_train_epoch_start)
            self.trainer.add_callback("on_train_epoch_end", self._on_train_epoch_end)
            self.trainer.add_callback("on_fit_epoch_end", self._on_fit_epoch_end)
            self.trainer.add_callback("on_train_end", self._on_train_end)

            self._task_info = task_info
            self._train_loss_path = task_info.task_dir / "train_loss"
            self._train_metric_path = task_info.task_dir / "train_metric"
            self._train_log_path = task_info.task_dir / "train.log"

            if self._train_log_path.exists() and self._train_parameters["resume"]:
                self._logs.load_log_from_text(self._train_log_path)
            else:
                self._logs.clear()

            if self._train_loss_path.exists() and self._train_parameters["resume"]:
                loss_data = pickle.load(open(self._train_loss_path, "rb"))
                self._loss_data.set_plot_data(loss_data)
            else:
                self._loss_data.clear_data()
            if self._train_metric_path.exists() and self._train_parameters["resume"]:
                metric_data = pickle.load(open(self._train_metric_path, "rb"))
                self._metric_data.set_plot_data(metric_data)
            else:
                self._metric_data.clear_data()

            return True
        except FileNotFoundError as e:
            error_msg = self.tr(
                "Resume checkpoint not found. Please pass a valid checkpoint to resume from,i.e model=path/to/last.pt")
            self.model_train_failed.emit(error_msg)
            self._logs.append(error_msg)
            return False

    def get_last_model(self):
        return self._last_model

    def get_train_parameters(self):
        return self._train_parameters

    def get_current_epoch(self) -> int:
        if self.trainer:
            return self.trainer.epoch
        return 0

    def _on_train_start(self, trainer):
        metrics = trainer.metrics
        loss_names = trainer.loss_names
        if self._loss_data.is_empty():
            self._loss_data.init_plot_data(loss_names)
        if self._metric_data.is_empty():
            self._metric_data.init_plot_data(metrics)
        self.train_start_signal.emit(self._loss_data.raw_data(), self._metric_data.raw_data())

    def _on_train_epoch_start(self, trainer):
        loss_names = trainer.loss_names
        info = f"{log_info(f' Epoch = {str(trainer.epoch + 1)}')}\n"
        info += f"{'Epoch' :<10}"
        for loss_name in loss_names:
            info += f"{loss_name:<10}"
        info += f"\n{'=' * 75}"
        self._logs.append(info)

    def _on_train_epoch_end(self, trainer):
        # epoch 从0 开始
        self._last_model = trainer.last.resolve().as_posix()
        self.train_epoch_end.emit(trainer.epoch + 1)
        self._current_epoch = trainer.epoch + 1

    def _on_fit_epoch_end(self, trainer):
        metrics = trainer.metrics
        self._metric_num += 1
        metrics_info = f"{self.tr('val result: ')}\n"
        metrics_info += f"{'Epoch':<10}"
        if self._metric_num > trainer.epoch + 1:
            metrics_info = f"{self.tr('test result: ')}\n"
        for metric_name in metrics.keys():
            metric_name = metric_name.split("/")[1]
            metrics_info += f"{metric_name:<15}"
        if self._metric_num == trainer.epoch + 1:
            epoch_format = f"\n{trainer.epoch + 1}/{trainer.epochs}"
            metrics_info += f"{epoch_format:<10}"
        else:
            metrics_info += "\n"
        for metric_value in metrics.values():
            metric_value = f"{metric_value: .4f}"
            metrics_info += f"{metric_value:<15}"
        metrics_info += "\n"

        self._metric_data.append(metrics)
        self._logs.append(metrics_info)

        self._loss_data.save_to_file(self._train_loss_path)
        self._metric_data.save_to_file(self._train_metric_path)
        self._logs.save_to_file(self._train_log_path)

    def _on_train_batch_start(self, trainer):
        trainer.interrupt = self._stop

    def _on_train_batch_end(self, trainer):
        batch_info_dict = trainer.pdic
        cur_batch = batch_info_dict["n"] + 1
        total_batch = batch_info_dict["total"]
        progress_percent = cur_batch / total_batch
        progress_bar_length = 30
        bar = '█' * int(progress_bar_length * progress_percent) + '-' * (
                progress_bar_length - int(progress_bar_length * progress_percent))

        # 生成进度条文本（这里使用简单的文本表示，你可以根据需要自定义）
        r_align = f"{progress_percent * 100:.2f}%".rjust(8)
        progress_bar_text = f"{r_align} |{bar}| {cur_batch}/{total_batch} "
        epoch_format = f"{trainer.epoch + 1}/{trainer.epochs}"
        batch_info = f"{epoch_format:<10}"
        loss_items = trainer.loss_items.cpu().numpy()
        if loss_items.ndim == 0:
            loss_item_value = f"{loss_items:.4f}"
            batch_info += f"{loss_item_value:<10}"
        else:
            for loss_item in loss_items:
                loss_item_value = f"{loss_item:.4f}"
                batch_info += f"{loss_item_value:<10}"
        batch_info += f"{progress_bar_text}"
        loss_names = trainer.loss_names
        if loss_items.ndim == 0:
            result_dict = {loss_names[0]: loss_items}
        else:
            result_dict = {k: k for k, v in zip(loss_names, loss_items)}

        self._loss_data.append(result_dict)
        self._logs.append(batch_info)

    def _on_train_end(self, trainer):
        current_epoch = trainer.epoch + 1
        if current_epoch == self._train_parameters["epochs"] and not self._stop:
            self._train_parameters["resume"] = ""
            self._task_info.task_status = TaskStatus.TRN_FINISHED
            self._logs.append(log_info(f"{self.tr('train finished')} epoch = {current_epoch}"))
        else:
            if self._last_model:
                self._train_parameters["resume"] = self._last_model
            self._task_info.task_status = TaskStatus.TRN_PAUSE
            self._logs.append(log_info(f"{self.tr('train finished ahead of schedule')} epoch = {current_epoch}"))
        self.model_train_end.emit(self._task_info)

    def run(self):
        if self.trainer:
            try:
                self.trainer.train()
            except Exception as e:
                self.model_train_failed.emit(str(e))

    @Slot()
    def stop_train(self):
        """在外部强制关闭线程？"""
        self._stop = True
