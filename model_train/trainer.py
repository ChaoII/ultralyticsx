from ultralytics import YOLO
from PySide6.QtCore import Slot, Signal, QThread

from common.utils import log_info

from ultralytics.models.yolo.classify import ClassificationTrainer


class ModelTrainThread(QThread):
    train_epoch_start_signal = Signal(str)
    train_batch_end_signal = Signal(str)
    train_epoch_end_signal = Signal(int, str)
    fit_epoch_end_signal = Signal(str)
    train_end_signal = Signal(int)

    def __init__(self, **kwargs):
        super(ModelTrainThread, self).__init__()

        self.trainer = ClassificationTrainer(overrides=kwargs)

        self.trainer.add_callback("on_train_batch_start", self._on_train_batch_start)
        self.trainer.add_callback("on_train_batch_end", self._on_train_batch_end)
        self.trainer.add_callback("on_train_epoch_start", self._on_train_epoch_start)
        self.trainer.add_callback("on_train_epoch_end", self._on_train_epoch_end)
        self.trainer.add_callback("on_fit_epoch_end", self._on_fit_epoch_end)
        self.trainer.add_callback("on_train_end", self._on_train_end)

        self._stop = False

    def _on_train_epoch_start(self, trainer):
        loss_names = trainer.loss_names

        print(loss_names)
        # info = f"{log_info(f' Epoch = {str(trainer.epoch + 1)}')}\n" \
        #        f"Epoch\t{loss_names[0]}\t{loss_names[1]}\t{loss_names[2]}\tloss\n" \
        #        f"{'=' * 75}"
        # self.train_epoch_start_signal.emit(info)

    def _on_train_epoch_end(self, trainer):
        # epoch 从0 开始
        self.train_epoch_end_signal.emit(trainer.epoch + 1, trainer.last.resolve().as_posix())

    def _on_fit_epoch_end(self, trainer):
        # metrics = trainer.metrics
        # if metrics.get("val/box_loss", -100) != -100:
        #     formatted_metrics = f"{self.tr('val result: ')} \n" \
        #                         f"Epoch\tprecision(B)\trecall(B)\tmAP50(B)\tmAP50-95(B)\tbox_loss\tcls_loss\tdfl_loss\n" \
        #                         f"{trainer.epoch + 1}/{trainer.epochs}\t{metrics['metrics/precision(B)']:.4f}\t" \
        #                         f"{metrics['metrics/recall(B)']:.4f}\t{metrics['metrics/mAP50(B)']:.4f}\t" \
        #                         f"{metrics['metrics/mAP50-95(B)']:.4f}\t{metrics.get('val/box_loss', 0.0):.4f}\t" \
        #                         f"{metrics['val/cls_loss']:.4f}\t{metrics['val/dfl_loss']:.4f}\n"
        #     self.fit_epoch_end_signal.emit(formatted_metrics)
        pass

    def _on_train_batch_start(self, trainer):
        trainer.interrupt = self._stop

    def _on_train_batch_end(self, trainer):
        # pdic = trainer.pdic
        # cur_batch = pdic["n"] + 1
        # total_batch = pdic["total"]
        # progress_percent = (cur_batch / total_batch) * 100
        #
        # # 生成进度条文本（这里使用简单的文本表示，你可以根据需要自定义）
        # r_align = f"{progress_percent:.2f}%".rjust(8)
        # progress_bar_text = f"{r_align} |{'█' * int(progress_percent / 5):<20}| {cur_batch}/{total_batch} "
        #
        # loss_items = trainer.loss_items.cpu().numpy()
        # loss = float(trainer.loss.cpu())
        #
        # batch_info = f"{trainer.epoch + 1}/{trainer.epochs}\t{loss_items[0]:.4f}\t{loss_items[0]:.4f}\t" \
        #              f"{loss_items[0]:.4f}\t{loss:.4f}\t{progress_bar_text}"
        #
        # self.train_batch_end_signal.emit(batch_info)
        pass

    def _on_train_end(self, trainer):
        self.train_end_signal.emit(trainer.epoch + 1)

    def run(self):
        self.trainer.train()

    @Slot()
    def stop_train(self):
        """在外部强制关闭线程？"""
        self._stop = True
