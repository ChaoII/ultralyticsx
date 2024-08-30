from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QVBoxLayout
from qfluentwidgets import TableWidget, SimpleCardWidget


class SplitLabelInfo:
    label: str
    all_num: int
    train_num: int
    val_num: int
    test_num: int

    def __init__(self, label, all_num, train_num, val_num, test_num):
        self.label = label
        self.all_num = all_num
        self.train_num = train_num
        self.val_num = val_num
        self.test_num = test_num


class LabelTableWidget(TableWidget):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(5)
        self.setRowCount(10)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setColumnWidth(0, 120)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 110)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._split_rates = []

    def set_split_rates(self, split_rates):
        self._split_rates = split_rates
        self.setHorizontalHeaderLabels([self.tr("Label name"), self.tr("Total data"),
                                        self.tr("Training set") + f"\n{split_rates[0]}%",
                                        self.tr("Validation set") + f"\n{split_rates[1]}%",
                                        self.tr("Testing set") + f"\n{split_rates[2]}%"])

    def set_data(self, dataset_split_num_info: list[SplitLabelInfo]):
        self.setRowCount(len(dataset_split_num_info))
        for index, dataset_num_info in enumerate(dataset_split_num_info):
            item0 = QTableWidgetItem(dataset_num_info.label)
            item1 = QTableWidgetItem(str(dataset_num_info.all_num))
            item2 = QTableWidgetItem(str(dataset_num_info.train_num))
            item3 = QTableWidgetItem(str(dataset_num_info.val_num))
            item4 = QTableWidgetItem(str(dataset_num_info.test_num))
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item3.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(index, 0, item0)
            self.setItem(index, 1, item1)
            self.setItem(index, 2, item2)
            self.setItem(index, 3, item3)
            self.setItem(index, 4, item4)


class ClassifyDatasetLabelsWidget(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(500)
        self.tb_label_info = LabelTableWidget()
        self.vly_dataset_info = QVBoxLayout(self)
        self.vly_dataset_info.addWidget(self.tb_label_info)

    def update_table(self, split_rates: list, dataset_split_num_info: list[SplitLabelInfo]):
        self.tb_label_info.set_split_rates(split_rates)
        self.tb_label_info.set_data(dataset_split_num_info)
