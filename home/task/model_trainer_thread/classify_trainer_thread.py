from PySide6.QtCore import Slot, Signal, QThread

from ultralytics.models.yolo.classify import ClassificationTrainer

from common.utils import log_info


class ModelTrainThread(QThread):
    train_start_signal = Signal(dict, list)
    train_epoch_start_signal = Signal(str)
    train_batch_end_signal = Signal(str, dict)
    train_epoch_end_signal = Signal(int, str)
    fit_epoch_end_signal = Signal(str, dict)
    train_end_signal = Signal(int,bool)
    model_train_failed = Signal(str)

    def __init__(self, train_parameters: dict):
        super(ModelTrainThread, self).__init__()

        self.trainer: ClassificationTrainer | None = None
        self._train_parameters = train_parameters
        self._stop = False
        self._metrics_num = -1

    def init_model_trainer(self) -> bool:
        try:
            self.trainer = ClassificationTrainer(overrides=self._train_parameters)
            self.trainer.add_callback("on_train_start", self._on_train_start)
            self.trainer.add_callback("on_train_batch_start", self._on_train_batch_start)
            self.trainer.add_callback("on_train_batch_end", self._on_train_batch_end)
            self.trainer.add_callback("on_train_epoch_start", self._on_train_epoch_start)
            self.trainer.add_callback("on_train_epoch_end", self._on_train_epoch_end)
            self.trainer.add_callback("on_fit_epoch_end", self._on_fit_epoch_end)
            self.trainer.add_callback("on_train_end", self._on_train_end)
            return True
        except FileNotFoundError as e:
            error_msg = self.tr(
                "Resume checkpoint not found. Please pass a valid checkpoint to resume from,i.e model=path/to/last.pt")
            self.model_train_failed.emit(error_msg)
            return False

    def _on_train_start(self, trainer):
        metrics = trainer.metrics
        loss_names = trainer.loss_names
        self.train_start_signal.emit(metrics, loss_names)

    def _on_train_epoch_start(self, trainer):
        loss_names = trainer.loss_names
        info = f"{log_info(f' Epoch = {str(trainer.epoch + 1)}')}\n"
        info += f"{'Epoch' :<10}"
        for loss_name in loss_names:
            info += f"{loss_name:<10}"
        info += f"\n{'=' * 75}"
        self.train_epoch_start_signal.emit(info)

    def _on_train_epoch_end(self, trainer):
        # epoch 从0 开始
        self.train_epoch_end_signal.emit(trainer.epoch + 1, trainer.last.resolve().as_posix())

    def _on_fit_epoch_end(self, trainer):
        metrics = trainer.metrics
        metrics_info = f"{self.tr('val result: ')}\n"
        metrics_info += f"{'Epoch':<10}"
        if 0 < self._metrics_num != len(metrics):
            metrics_info = f"{self.tr('test result: ')}\n"
        self.metrics_num = len(metrics)
        for metric_name in metrics.keys():
            metric_name = metric_name.split("/")[1]
            metrics_info += f"{metric_name:<15}"
        if 0 < self.metrics_num == len(metrics):
            epoch_format = f"\n{trainer.epoch + 1}/{trainer.epochs}"
            metrics_info += f"{epoch_format:<10}"
        for metric_value in metrics.values():
            metric_value = f"{metric_value: .4f}"
            metrics_info += f"{metric_value:<15}"
        metrics_info += "\n"
        self.fit_epoch_end_signal.emit(metrics_info, metrics)

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
        self.train_batch_end_signal.emit(batch_info, result_dict)

    def _on_train_end(self, trainer):
        self.train_end_signal.emit(trainer.epoch + 1, self._stop)

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