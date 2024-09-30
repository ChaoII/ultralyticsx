import sys
from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, \
    OptionsValidator, FolderValidator, ConfigSerializer


def is_win11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Language.Chinese, QLocale.Country.HongKong)
    ENGLISH = QLocale(QLocale.Language.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # model
    workspace_folder = ConfigItem(
        "model", "workspace_dir", "./", FolderValidator())
    enable_tensorboard = ConfigItem(
        "model", "enable_tensorboard", False, BoolValidator())

    # main window
    enable_mica_effect = ConfigItem(
        "personalization", "enable_mica_effect", is_win11(), BoolValidator())
    minimize_to_tray = ConfigItem(
        "personalization", "minimize_to_tray", True, BoolValidator())
    dpi_scale = OptionsConfigItem(
        "personalization", "dpi_scale", "auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "auto"]), restart=True)
    language = OptionsConfigItem(
        "personalization", "language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    remember_quit_status = ConfigItem(
        "personalization", "remember_quit_status", False, BoolValidator())


cfg = Config()
qconfig.load('settings/config.json', cfg)
