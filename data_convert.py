from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QPushButton, QGroupBox, QGridLayout,
                               QLabel, QLineEdit, QFileDialog)

from PySide6.QtCore import Slot
from utils import convert


class DataConvertWidget(QWidget):
    def __init__(self):
        super(DataConvertWidget, self).__init__()

        h_layout = QHBoxLayout()
        self.led_file_path = QLineEdit()
        btn_load_dataset = QPushButton(text="选择数据集文件")
        btn_data_valid = QPushButton(text="数据校验")
        h_layout.addWidget(self.led_file_path)
        h_layout.addWidget(btn_load_dataset)

        gly = QGridLayout()
        self.lbl_train_img_num = QLabel()
        self.lbl_train_obj_num = QLabel()
        self.lbl_val_img_num = QLabel()
        self.lbl_val_obj_num = QLabel()
        self.lbl_test_img_num = QLabel()
        self.lbl_test_obj_num = QLabel()

        gb_train_image_num = QGroupBox("训练集图片数量")
        vly_train_image_num = QVBoxLayout()
        vly_train_image_num.addWidget(self.lbl_train_img_num)
        gb_train_image_num.setLayout(vly_train_image_num)

        gb_train_obj_num = QGroupBox("训练集对象数量")
        vly_train_obj_num = QVBoxLayout()
        vly_train_obj_num.addWidget(self.lbl_train_obj_num)
        gb_train_obj_num.setLayout(vly_train_obj_num)

        gb_val_image_num = QGroupBox("验证集图片数量")
        vly_val_image_num = QVBoxLayout()
        vly_val_image_num.addWidget(self.lbl_val_img_num)
        gb_val_image_num.setLayout(vly_val_image_num)

        gb_val_obj_num = QGroupBox("验证集对象数量")
        vly_val_obj_num = QVBoxLayout()
        vly_val_obj_num.addWidget(self.lbl_val_obj_num)
        gb_val_obj_num.setLayout(vly_val_obj_num)

        gb_test_image_num = QGroupBox("测试集图片数量")
        vly_test_image_num = QVBoxLayout()
        vly_test_image_num.addWidget(self.lbl_test_img_num)
        gb_test_image_num.setLayout(vly_test_image_num)

        gb_test_obj_num = QGroupBox("测试集对象数量")
        vly_test_obj_num = QVBoxLayout()
        vly_test_obj_num.addWidget(self.lbl_test_obj_num)
        gb_test_obj_num.setLayout(vly_test_obj_num)
        gly.addWidget(gb_train_image_num, 0, 0)
        gly.addWidget(gb_train_obj_num, 0, 1)
        gly.addWidget(gb_val_image_num, 1, 0)
        gly.addWidget(gb_val_obj_num, 1, 1)
        gly.addWidget(gb_test_image_num, 2, 0)
        gly.addWidget(gb_test_obj_num, 2, 1)

        self.led_dataset_config_path = QLabel()
        gb_dataset_config_path = QGroupBox("数据集配置文件路径")
        vly_dataset_config_path = QVBoxLayout()
        vly_dataset_config_path.addWidget(self.led_dataset_config_path)
        gb_dataset_config_path.setLayout(vly_dataset_config_path)

        self.ted_dataset_labels = QLabel()
        self.ted_dataset_labels.setEnabled(False)
        gb_dataset_labels = QGroupBox("数据集标签")
        vly_dataset_labels = QVBoxLayout()
        vly_dataset_labels.addWidget(self.ted_dataset_labels)
        gb_dataset_labels.setLayout(vly_dataset_labels)
        gb_dataset_labels.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        v_layout = QVBoxLayout(self)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(btn_data_valid)
        v_layout.addLayout(gly)
        v_layout.addWidget(gb_dataset_config_path)
        v_layout.addWidget(gb_dataset_labels)

        btn_load_dataset.clicked.connect(self.open_file)
        btn_data_valid.clicked.connect(self.data_valid)

    @Slot()
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开数据集文件目录", "", "All Files (*);;")
        self.led_file_path.setText(file_name)

    @Slot()
    def data_valid(self):
        (dataset_dir, train_image_num, train_obj_num, val_image_num, val_obj_num,
         test_image_num, test_obj_num, labels, dst_yaml_path) = convert(self.led_file_path.text())
        self.lbl_train_img_num.setText(str(train_image_num))
        self.lbl_train_obj_num.setText(str(train_obj_num))
        self.lbl_val_img_num.setText(str(val_image_num))
        self.lbl_val_obj_num.setText(str(val_obj_num))
        self.lbl_test_img_num.setText(str(test_image_num))
        self.lbl_test_obj_num.setText(str(test_obj_num))
        self.led_dataset_config_path.setText(dst_yaml_path)
        self.ted_dataset_labels.setText(str(labels))
