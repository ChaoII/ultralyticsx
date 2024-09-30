from PySide6.QtWidgets import QWidget


class ContentWidgetBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def update_widget(self):
        raise NotImplementedError
