# coding:utf-8
from .config import cfg
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard, BodyLabel,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIco
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths
from PySide6.QtWidgets import QFrame, QLabel, QFontDialog, QFileDialog


class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = Signal()
    musicFoldersChanged = Signal(list)
    acrylicEnableChanged = Signal(bool)
    downloadFolderChanged = Signal(str)
    minimizeToTrayChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName("setting_interface")
        self.scrollWidget = QFrame()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # model
        self.model_config_group = SettingCardGroup(
            self.tr("model settings"), self.scrollWidget)

        self.workspace_folder_card = PushSettingCard(
            text=self.tr('choose folder'),
            icon=FIco.FOLDER,
            title=self.tr("workspace folder"),
            content=cfg.get(cfg.workspace_folder),
            parent=self.model_config_group
        )

        self.enable_tensorboard_card = SwitchSettingCard(
            FIco.MARKET,
            self.tr("enable tensorboard"),
            self.tr("use tensorboard to monitor training step"),
            configItem=cfg.enable_tensorboard,
            parent=self.model_config_group
        )

        # personalization
        self.personal_group = SettingCardGroup(self.tr('personalization'), self.scrollWidget)
        self.enable_acrylic_ard = SwitchSettingCard(
            FIco.TRANSPARENT,
            self.tr("Use Acrylic effect"),
            self.tr("Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=cfg.enable_acrylic_background,
            parent=self.personal_group
        )
        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            FIco.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personal_group
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor,
            FIco.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personal_group
        )
        self.zoom_card = OptionsSettingCard(
            cfg.dpi_scale,
            FIco.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personal_group
        )
        self.language_card = ComboBoxSettingCard(
            cfg.language,
            FIco.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personal_group
        )

        # main panel
        self.main_panel_group = SettingCardGroup(self.tr('Main Panel'), self.scrollWidget)
        self.minimize_to_tray_card = SwitchSettingCard(
            FIco.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('PyQt-Fluent-Widgets will continue to run in the background'),
            configItem=cfg.minimize_to_tray,
            parent=self.main_panel_group
        )

        self._init_widget()

    def _init_widget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 20, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self._set_qss()

        # initialize layout
        self._init_layout()
        self._connect_signal_to_slot()

    def _init_layout(self):
        # self.settingLabel.move(60, 63)

        # add cards to group
        self.model_config_group.addSettingCard(self.workspace_folder_card)
        self.model_config_group.addSettingCard(self.enable_tensorboard_card)

        self.personal_group.addSettingCard(self.enable_acrylic_ard)
        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)
        self.personal_group.addSettingCard(self.zoom_card)
        self.personal_group.addSettingCard(self.language_card)

        self.main_panel_group.addSettingCard(self.minimize_to_tray_card)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.model_config_group)
        self.expandLayout.addWidget(self.personal_group)
        self.expandLayout.addWidget(self.main_panel_group)

    def _set_qss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _show_restart_tooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        font, is_ok = QFontDialog.getFont(
            cfg.desktopLyricFont, self.window(), self.tr("Choose font"))
        if is_ok:
            cfg.desktopLyricFont = font

    def _on_workspace_folder_card_clicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.workspace_folder) == folder:
            return

        cfg.set(cfg.workspace_folder, folder)
        self.workspace_folder_card.setContent(folder)

    def _on_Theme_changed(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self._set_qss()

    def _connect_signal_to_slot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self._show_restart_tooltip)
        cfg.themeChanged.connect(self._on_Theme_changed)

        # model
        self.workspace_folder_card.clicked.connect(
            self._on_workspace_folder_card_clicked)

        self.enable_tensorboard_card.checkedChanged.connect(
            self.acrylicEnableChanged)

        # personalization
        self.enable_acrylic_ard.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.theme_color_card.colorChanged.connect(setThemeColor)

        # main panel
        self.minimize_to_tray_card.checkedChanged.connect(
            self.minimizeToTrayChanged)
