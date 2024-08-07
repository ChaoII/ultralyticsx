import sys
from PySide6.QtWidgets import (QApplication,
                               QVBoxLayout, QWidget,
                               QFileDialog, QTabWidget)
from PySide6.QtCore import Slot
from dataset_process.data_convert import DataConvertWidget
from model_train import ModelTrainWidget
from config_widget import ConfigWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(800, 600)
        self.setWindowTitle('Model Training and Prediction')
        self.data_convert_widget = DataConvertWidget()
        self.model_train_widget = ModelTrainWidget()
        self.config_widget = ConfigWidget()
        layout = QVBoxLayout(self)
        tab_widget = QTabWidget()
        tab_widget.addTab(self.data_convert_widget, "数据转换")
        tab_widget.addTab(self.model_train_widget, "模型训练")
        tab_widget.addTab(self.config_widget, "参数配置")

        layout.addWidget(tab_widget)



    @Slot()
    def load_data(self):
        # 这里可以添加打开文件对话框来加载数据
        print("Loading data...")

    @Slot()
    def train_model(self):
        # 假设数据已加载到某个地方
        data = "dummy_data"

    @Slot()
    def save_model(self):
        # 打开文件保存对话框
        path, _ = QFileDialog.getSaveFileName(self, "Save Model", "", "Model Files (*.model)")

    @Slot()
    def predict(self):
        input_data = self.input_line.text()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
