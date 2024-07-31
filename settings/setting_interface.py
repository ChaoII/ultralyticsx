# coding:utf-8
from .config import cfg
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard, BodyLabel,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths
from PySide6.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog


class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = Signal()
    musicFoldersChanged = Signal(list)
    acrylicEnableChanged = Signal(bool)
    downloadFolderChanged = Signal(str)
    minimizeToTrayChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = BodyLabel(self.tr("Settings"), self)

        # model
        self.model_config_group = SettingCardGroup(
            self.tr("model settings"), self.scrollWidget)

        self.downloadFolderCard = PushSettingCard(
            text=self.tr('choose folder'),
            icon=FIF.DOWNLOAD,
            title=self.tr("workspace folder"),
            content=cfg.get(cfg.workspace_folder),
            parent=self.model_config_group
        )

        # self.musicFolderCard = FolderListSettingCard(
        #     cfg.workspace_folder,
        #     self.tr("Local music library"),
        #     directory=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation),
        #     parent=self.model_config_group
        # )
        # self.downloadFolderCard = PushSettingCard(
        #     self.tr('Choose folder'),
        #     FIF.DOWNLOAD,
        #     self.tr("Download directory"),
        #     cfg.get(cfg.downloadFolder),
        #     self.model_config_group
        # )

        # personalization
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.enableAcrylicCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Use Acrylic effect"),
            self.tr("Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=cfg.enableAcrylicBackground,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # main panel
        self.mainPanelGroup = SettingCardGroup(self.tr('Main Panel'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('PyQt-Fluent-Widgets will continue to run in the background'),
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        # add cards to group
        self.musicInThisPCGroup.addSettingCard(self.musicFolderCard)
        self.musicInThisPCGroup.addSettingCard(self.downloadFolderCard)

        self.personalGroup.addSettingCard(self.enableAcrylicCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.musicInThisPCGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            cfg.desktopLyricFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.desktopLyricFont = font

    def __onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # music in the pc
        self.musicFolderCard.folderChanged.connect(
            self.musicFoldersChanged)
        self.downloadFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked)

        # personalization
        self.enableAcrylicCard.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)

        # main panel
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)
