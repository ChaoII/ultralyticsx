from pathlib import Path

from PySide6.QtCore import QObject, Qt
from qfluentwidgets import StrongBodyLabel, MessageBoxBase, InfoBar, InfoBarPosition, BodyLabel

from common.component.file_select_widget import FileSelectWidget
from common.component.progress_message_box import ProgressMessageBox
from common.core.window_manager import window_manager
from home.task.task_thread.model_predict_thread import ModelPredictorThread
from ultralytics.engine.results import Results


class SemiAutomaticAnnotationEnsureMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = StrongBodyLabel(self.tr("Select a annotation model file"), self)
        self.cus_file_select_widget = FileSelectWidget(is_dir=False, file_filter="All Files (*);;Model Files (*.pt)")
        self.lbl_warning = BodyLabel(self.tr(
            "Warning: Once the semi-automatic annotation is confirmed, the semi-automatic "
            "annotation result will override the manual annotation result, please choose carefully!"), self)
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.setTextColor(Qt.GlobalColor.red, Qt.GlobalColor.red)
        # 将组件添加到布局中
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.cus_file_select_widget)
        self.viewLayout.addWidget(self.lbl_warning)

    def get_model_path(self):
        return self.cus_file_select_widget.text()


class ModelPredict(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model_predict_thread: ModelPredictorThread | None = None
        self._message_box: ProgressMessageBox | None = None
        self._is_compact = False

    def create_predict_thread(self, model_path: Path):
        self._model_predict_thread = ModelPredictorThread(model_path)
        self._model_predict_thread.model_predict_end.connect(self._on_predict_end)
        self._model_predict_thread.model_predict_failed.connect(self._on_predict_failed)

    def _close_message_box(self, is_error: bool = False):
        if self._message_box:
            if is_error:
                self._message_box.set_error(True)
            self._message_box.close()

    def predict(self, model_path: Path, image_path: Path) -> Results | None:
        self.create_predict_thread(model_path)
        self._model_predict_thread.set_predict_image(image_path)
        self._model_predict_thread.start()
        self._message_box = ProgressMessageBox(indeterminate=True, parent=window_manager.find_window("main_widget"))
        self._message_box.set_ring_size(100, 100)
        self._message_box.exec()
        return self.result

    def _on_predict_failed(self, err_msg: str):
        self._close_message_box(is_error=True)
        InfoBar.error(
            title="",
            content=err_msg,
            duration=-1,
            position=InfoBarPosition.TOP_RIGHT,
            parent=window_manager.find_window("main_widget")
        )

    def _on_predict_end(self, result: Results):
        self.result = result
        self._close_message_box()
        InfoBar.success(
            title="",
            content=self.tr("Predict successfully"),
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=window_manager.find_window("main_widget")
        )
