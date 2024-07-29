import os

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QCheckBox, QLineEdit, QFileDialog,
                               QSpacerItem)
from PySide6.QtCore import Qt
import yaml
from PySide6.QtCore import Slot
from pathlib import Path
from ultralytics import settings


class ConfigWidget(QWidget):
    def __init__(self):
        super(ConfigWidget, self).__init__()

        h_layout = QHBoxLayout()
        self.led_workspace_path = QLineEdit()
        btn_load_dataset = QPushButton(text="选择工作目录")
        h_layout.addWidget(self.led_workspace_path)
        h_layout.addWidget(btn_load_dataset)
        self.cb_open_tb = QCheckBox("开启TensorBoard")

        h_layout1 = QHBoxLayout()
        btn_save_config = QPushButton(text="保存配置")
        h_layout1.addStretch(1)
        h_layout1.addWidget(btn_save_config)

        v_layout = QVBoxLayout(self)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.cb_open_tb)
        v_layout.addStretch(1)
        v_layout.addLayout(h_layout1)

        btn_load_dataset.clicked.connect(self.open_directory)
        btn_save_config.clicked.connect(self.save_config)
        self.cb_open_tb.checkStateChanged.connect(self.update_tb_status)

        self.config = None
        self._init_config_file()
        self.setup_ui()

    def _init_config_file(self):
        if not Path("config.yaml").exists():
            self.config = dict()
            self.config["Base"] = dict()
            self.config["Base"]["workspace_dir"] = os.getcwd()
            self.config["Base"]["with_tensorboard"] = False
        else:
            with open("config.yaml", encoding="utf8", mode="r") as f:
                self.config = yaml.safe_load(f)
                if self.config is None:
                    print("请指定正确的配置文件")
            settings.update({"runs_dir": self.config["Base"]["workspace_dir"], "tensorboard": False})

    def setup_ui(self):
        if self.config and self.config["Base"]:
            self.led_workspace_path.setText(self.config["Base"]["workspace_dir"])
            self.cb_open_tb.setChecked(self.config["Base"]["with_tensorboard"])

    @Slot()
    def update_tb_status(self, check_status: Qt.CheckState):
        self.config["Base"]["with_tensorboard"] = check_status == Qt.CheckState.Checked

    @Slot()
    def open_directory(self):
        workspace = QFileDialog.getExistingDirectory(self, "选择工作目录")
        self.led_workspace_path.setText(workspace)
        if self.config["Base"] is not None:
            self.config["Base"] = {"workspace_dir": Path(workspace).resolve().as_posix()}

    @Slot()
    def save_config(self):
        settings.update(
            {"runs_dir": self.config["Base"]["workspace_dir"], "with_tensorboard": self.cb_open_tb.isChecked()})
        with open('config.yaml', encoding="utf8", mode='w') as stream:
            yaml.safe_dump(self.config, stream, default_flow_style=False)
