from PySide6.QtWidgets import QListWidget
from qfluentwidgets import isDarkTheme, SmoothScrollDelegate

from settings import cfg


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollDelegate = SmoothScrollDelegate(self)
        self.item_height = 35
        self.item_hover_color = "rgba(255,255,255,20)"
        if isDarkTheme():
            self.item_pressed_color = "rgba(255,255,255,15)"
        else:
            self.item_pressed_color = "rgba(255,255,255,9)"
        self.update_style_sheet()

    def disable_hover_effect(self):
        self.item_hover_color = "transparent"
        self.update_style_sheet()

    def connect_signals_and_slots(self):
        cfg.themeChanged.connect(self.on_theme_changed)

    def on_theme_changed(self):
        self.item_pressed_color = "rgba(255,255,255,9)"
        self.update_style_sheet()

    def set_item_height(self, item_height):
        self.item_height = item_height
        self.update_style_sheet()

    def update_style_sheet(self) -> None:
        self.setStyleSheet(f"""
                    CustomListWidget {{
                        background: transparent;
                        outline: none;
                        border: none;
                        /* font: 13px 'Segoe UI', 'Microsoft YaHei'; */
                        selection-background-color: transparent;
                        alternate-background-color: transparent;
                        padding-left: 4px;
                        padding-right: 4px;
                    }}
                    CustomListWidget::item {{
                        background: transparent;
                        border: 0px;
                        padding-left: 11px;
                        padding-right: 11px;
                        height: {self.item_height}px;
                    }}
                    CustomListWidget::item::hover {{
                        width: 18px;
                        height: 18px;
                        border-radius: 5px;
                        border: none;
                        background-color: {self.item_hover_color};
                        margin-right: 4px;
                    }}
                    CustomListWidget::item::selected {{
                        width: 18px;
                        height: 18px;
                        border-radius: 5px;
                        border: none;
                        background-color: {self.item_pressed_color};
                        margin-right: 4px;
                    }}
                    """)
