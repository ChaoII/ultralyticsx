from PySide6.QtCore import Slot, Signal, QThread

from ultralytics.models.yolo.classify import ClassificationTrainer

from common.utils import log_info


class ModelTrainThread(QThread):
    train_epoch_start_signal = Signal(str)
    train_batch_end_signal = Signal(str)
    train_epoch_end_signal = Signal(int, str)
    fit_epoch_end_signal = Signal(str)
    train_end_signal = Signal(int)

    def __init__(self, train_parameters: dict):
        super(ModelTrainThread, self).__init__()

        self.trainer = ClassificationTrainer(overrides=train_parameters)

        self.trainer.add_callback("on_train_batch_start", self._on_train_batch_start)
        self.trainer.add_callback("on_train_batch_end", self._on_train_batch_end)
        self.trainer.add_callback("on_train_epoch_start", self._on_train_epoch_start)
        self.trainer.add_callback("on_train_epoch_end", self._on_train_epoch_end)
        self.trainer.add_callback("on_fit_epoch_end", self._on_fit_epoch_end)
        self.trainer.add_callback("on_train_end", self._on_train_end)

        self._stop = False
        self.metrics_num = -1

    def _on_train_epoch_start(self, trainer):
        loss_names = trainer.loss_names
        info = f"{log_info(f' Epoch = {str(trainer.epoch + 1)}')}\nEpoch\t"
        for loss_name in loss_names:
            info += f"{loss_name}\t"
        info += f"\n{'=' * 75}\n\t"
        self.train_epoch_start_signal.emit(info)

    def _on_train_epoch_end(self, trainer):
        # epoch 从0 开始
        self.train_epoch_end_signal.emit(trainer.epoch + 1, trainer.last.resolve().as_posix())

    def _on_fit_epoch_end(self, trainer):
        metrics = trainer.metrics
        metrics_info = f"{self.tr('val result: ')} \n"
        metrics_info += "Epoch\t"
        if 0 < self.metrics_num != len(metrics):
            metrics_info = f"{self.tr('test result: ')} \n"
        self.metrics_num = len(metrics)

        for metric_name in metrics.keys():
            metric_name = metric_name.split("/")[1]
            metrics_info += f"{metric_name}\t"
        metrics_info += f"\n{trainer.epoch + 1}/{trainer.epochs}\t"
        for metric_value in metrics.values():
            metrics_info += f"{metric_value:.4f}\t\t"
        metrics_info += "\n"
        self.fit_epoch_end_signal.emit(metrics_info)

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
        batch_info = f"{trainer.epoch + 1}/{trainer.epochs}\t"
        loss_items = trainer.loss_items.cpu().numpy()
        if loss_items.ndim == 0:
            batch_info += f"{loss_items:.4f}\t"
        else:
            for loss in loss_items:
                batch_info += f"{loss:.4f}\t"
        batch_info += f"{progress_bar_text}"
        self.train_batch_end_signal.emit(batch_info)

    def _on_train_end(self, trainer):
        self.train_end_signal.emit(trainer.epoch + 1)

    def run(self):
        self.trainer.train()

    @Slot()
    def stop_train(self):
        """在外部强制关闭线程？"""
        self._stop = True
