from PySide6.QtGui import QColor
from qfluentwidgets import HyperlinkLabel, setCustomStyleSheet, BodyLabel


class CustomLabel(BodyLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setText(text)

    def setTextColor(self, light=QColor(0, 0, 0), dark=QColor(255, 255, 255)):
        setCustomStyleSheet(
            self,
            f"CustomLabel{{color:{light.name(QColor.NameFormat.HexArgb)}}}",
            f"CustomLabel{{color:{dark.name(QColor.NameFormat.HexArgb)}}}"
        )
