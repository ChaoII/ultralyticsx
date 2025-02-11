from PySide6.QtCore import QPaginator, Q_ARG, Signal
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


class PaginatedDataView(QWidget):
    def __init__(self, data_list, items_per_page=10):
        super().__init__()
        self.data_list = data_list
        self.items_per_page = items_per_page
        self.paginator = QPaginator(len(data_list), self)
        self.paginator.currentPageChanged.connect(self.show_current_page)
        self.current_page_label = QLabel("Page 0/0")
        self.data_layout = QVBoxLayout()
        self.setLayout(self.data_layout)

        # 初始化分页显示
        self.show_current_page(0)

    def show_current_page(self, page_number):
        start_index = page_number * self.items_per_page
        end_index = min((page_number + 1) * self.items_per_page, len(self.data_list))
        page_data = self.data_list[start_index:end_index]

        # 更新UI显示当前页数据
        for i, data in enumerate(page_data):
            label = QLabel(str(data))
            if self.data_layout.count() > i:
                self.data_layout.itemAt(i).widget().deleteLater()
                self.data_layout.takeAt(i)
            self.data_layout.insertWidget(i, label)

        # 更新页码显示
        self.current_page_label.setText(f"Page {page_number + 1}/{self.paginator.numPages()}")


# 使用示例
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # 创建一个包含数据的列表
    data_list = list(range(100))  # 假设有100项数据

    # 创建分页视图并显示
    paginated_view = PaginatedDataView(data_list)
    paginated_view.show()

    sys.exit(app.exec())