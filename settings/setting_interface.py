from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout
from qfluentwidgets import FluentIcon as FIco
from qfluentwidgets import SettingCardGroup, SwitchSettingCard, OptionsSettingCard, PushSettingCard, \
    ComboBoxSettingCard, InfoBar, CustomColorSettingCard, setTheme, setThemeColor

from common.component.custom_scroll_widget import CustomScrollWidget
from .config import cfg, is_win11


class SettingInterface(QWidget):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("setting_interface")
        self.scroll_area = CustomScrollWidget()
        self.vly_config_card = QVBoxLayout()

        # model
        self.model_config_group = SettingCardGroup(
            self.tr("Model settings"), self.scroll_area)
        self.workspace_dir_card = PushSettingCard(
            text=self.tr('Choose directory'),
            icon=FIco.FOLDER,
            title=self.tr("Workspace directory"),
            content=cfg.get(cfg.workspace_dir),
            parent=self.model_config_group
        )

        # personalization
        self.personal_group = SettingCardGroup(self.tr('Personalization'), self.scroll_area)
        self.enable_mica_card = SwitchSettingCard(
            FIco.TRANSPARENT,
            self.tr("Use Mica effect"),
            self.tr("Windows and surfaces appear translucent"),
            configItem=cfg.enable_mica_effect,
            parent=self.personal_group
        )
        self.enable_mica_card.setEnabled(is_win11())
        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            FIco.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of the application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Follow system setting')
            ],
            parent=self.personal_group
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor,
            FIco.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of the application'),
            self.personal_group
        )
        self.zoom_card = OptionsSettingCard(
            cfg.dpi_scale,
            FIco.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Follow system setting")
            ],
            parent=self.personal_group
        )
        self.language_card = ComboBoxSettingCard(
            cfg.language,
            FIco.LANGUAGE,
            self.tr('Language'),
            self.tr('Change the preferred language of the application'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Follow system setting')],
            parent=self.personal_group
        )

        # main panel
        self.main_panel_group = SettingCardGroup(self.tr('Main Panel'), self.scroll_area)
        self.minimize_to_tray_card = SwitchSettingCard(
            FIco.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('Ultraly UI will continue to run in the background'),
            configItem=cfg.minimize_to_tray,
            parent=self.main_panel_group
        )


        self.model_config_group.addSettingCard(self.workspace_dir_card)

        self.personal_group.addSettingCard(self.enable_mica_card)
        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)
        self.personal_group.addSettingCard(self.zoom_card)
        self.personal_group.addSettingCard(self.language_card)
        self.main_panel_group.addSettingCard(self.minimize_to_tray_card)

        self.vly_config_card.setSpacing(28)
        self.vly_config_card.setContentsMargins(20, 10, 20, 0)
        self.vly_config_card.addWidget(self.model_config_group)
        self.vly_config_card.addWidget(self.personal_group)
        self.vly_config_card.addWidget(self.main_panel_group)
        self.scroll_area.setLayout(self.vly_config_card)

        self.vly_content = QVBoxLayout(self)
        self.vly_content.addWidget(self.scroll_area)

        self._connect_signal_to_slot()

    def _show_restart_tooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def _on_workspace_directory_card_clicked(self):
        """ workspace directory card clicked slot """
        directory = QFileDialog.getExistingDirectory(
            self, self.tr("Workspace directory"), "./")
        if not directory or cfg.get(cfg.workspace_directory) == directory:
            return
        cfg.set(cfg.workspace_directory, directory)

        self.workspace_dir_card.setContent(directory)


    def _connect_signal_to_slot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self._show_restart_tooltip)
        cfg.themeChanged.connect(lambda theme: setTheme(theme))

        # model
        self.workspace_dir_card.clicked.connect(self._on_workspace_directory_card_clicked)
        self.theme_color_card.colorChanged.connect(setThemeColor)
