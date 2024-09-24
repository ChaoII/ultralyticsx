from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, \
    OptionsValidator, FolderValidator, ConfigSerializer


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
    enable_acrylic_background = ConfigItem(
        "personalization", "enable_acrylic_background", False, BoolValidator())
    minimize_to_tray = ConfigItem(
        "personalization", "minimize_to_tray", True, BoolValidator())
    dpi_scale = OptionsConfigItem(
        "personalization", "dpi_scale", "auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "auto"]), restart=True)
    language = OptionsConfigItem(
        "personalization", "language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)


cfg = Config()
qconfig.load('settings/config.json', cfg)
