from tkinter import ttk
from tkinter import font as tkfont

from PIL import ImageTk, Image

style = None


def getStyleFontFromTkFont(font):
    return f"{font.cget('family')} {str(font.cget('size'))} {font.cget('weight')}"


def copyFontWithOptions(font, **kwargs):
    copy = font.copy()
    copy.config(**kwargs)
    return copy


radiobuttonEmpty = None
radiobuttonSelected = None

blueRadiobuttonEmpty = None
blueRadiobuttonSelected = None

checkboxEmpty = None
checkboxSelected = None

trashIcon = None

upIcon = None
topIcon = None
downIcon = None
bottomIcon = None

standbyImg = None
operateImg = None
largeStandbyImg = None
largeOperateImg = None

tunemodeDisabledImg = None
tunemodeOffImg = None
tunemodeOnImg = None

resetOnImg = None
resetOffImg = None
resetErrorImg = None
largeResetOffImg = None
largeResetOnImg = None

def initThemes(app):
    global style
    style = ttk.Style()
    defaultBgColor = style.lookup("TFrame", "background")

    standardFont = tkfont.Font(family="Lato")
    font_very_tiny = copyFontWithOptions(standardFont, size=9)
    font_tiny_bold = copyFontWithOptions(standardFont, size=12, weight="bold")
    font_small_bold = copyFontWithOptions(standardFont, size=14, weight="bold")
    font_medium_bold = copyFontWithOptions(standardFont, size=16, weight="bold")
    font_large_bold = copyFontWithOptions(standardFont, size=18, weight="bold")
    font_huge_bold = copyFontWithOptions(standardFont, size=20, weight="bold")
    font_very_huge_bold = copyFontWithOptions(standardFont, size=24, weight="bold")
    font_giant_bold = copyFontWithOptions(standardFont, size=30, weight="bold")
    font_very_huge = copyFontWithOptions(standardFont, size=24)
    font_large = copyFontWithOptions(standardFont, size=18)


    style.theme_create("custom_dark", parent="clam")
    style.theme_use("custom_dark")

    # Main
    style.configure("TFrame", background="#000000")
    style.configure("TButton", font=getStyleFontFromTkFont(font_small_bold), background="#000000", foreground="#ffffff", anchor="CENTER")
    style.configure("Huge.TButton", font=getStyleFontFromTkFont(font_very_huge_bold))
    style.configure("Button.Huge.TButton", borderwidth=5, relief="groove", anchor="CENTER", background='#888888', foreground="#000000")
    style.configure("TLabel", font=getStyleFontFromTkFont(font_small_bold), background="#000000", foreground="#ffffff")
    style.configure("Huge.TLabel", font=getStyleFontFromTkFont(font_very_huge_bold))
    style.configure("Scale.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Huge.Scale.TLabel", font=getStyleFontFromTkFont(font_very_huge_bold))
    style.configure("Value.Scale.TLabel", font=getStyleFontFromTkFont(font_medium_bold))
    style.configure("Value.Huge.Scale.TLabel", font=getStyleFontFromTkFont(font_huge_bold))
    style.configure("Status.TLabel", foreground="#ff0000", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Huge.Status.TLabel", foreground="#ff0000", font=getStyleFontFromTkFont(font_giant_bold))
    style.configure("Large.OperatingButton.TLabel", font=getStyleFontFromTkFont(font_huge_bold))
    style.configure("Filter.TLabel", background="#e6d875", foreground="#000000", font=getStyleFontFromTkFont(font_tiny_bold))
    style.map("Filter.TLabel", background=[("active", "#b36f19")])
    style.configure("Antenna.Toolbutton", foreground="#ffffff", background='#666666',
                    font=getStyleFontFromTkFont(font_large_bold))
    style.map("Antenna.Toolbutton", foreground=[("selected", '#00ff00'), ("disabled", '#888888')],
              background=[("disabled", '#333333')])
    style.configure("Selected.Antenna.Toolbutton.TFrame", background='#666666')
    style.configure("Antenna.Toolbutton.TLabel", background='#666666',
                    font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Selected.Antenna.Toolbutton.TLabel", foreground='#ffff00')

    style.configure("Band.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Yellow.Band.TLabel", foreground="#ffff00")
    style.configure("Hardware.TLabel", padding=(10, 0))
    style.configure("Green.Hardware.TLabel", foreground="#00ff00")
    style.configure("Yellow.Hardware.TLabel", foreground="#ffff00")
    style.configure("Red.HardwareStat.TLabel", foreground="#00ff00")
    style.configure("Menu.TLabel", foreground="#ff0000", borderwidth=1, bordercolor="#ff0000", relief="solid")
    style.configure("Device.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Custom.Device.TLabel", font=getStyleFontFromTkFont(font_huge_bold), foreground="#ffff00")
    style.configure("Interface.TLabel", font=getStyleFontFromTkFont(font_large_bold), foreground="#00ff00")
    style.configure("Warning.Status.TLabel", foreground="#ffff00")
    style.configure("Warning.Huge.Status.TLabel", foreground="#ffff00")
    style.configure("Active.Status.TLabel",  foreground="#00ff00")
    style.configure("Inactive.Status.TLabel", foreground="#000000")
    style.configure("Frequency.TLabel", font=getStyleFontFromTkFont(font_huge_bold))
    style.configure("Header.Tuner.TLabel", font=getStyleFontFromTkFont(font_tiny_bold), foreground="#00ff00")
    style.configure("Invisible.Header.Tuner.TLabel", font=getStyleFontFromTkFont(font_tiny_bold), foreground="#000000")
    style.configure("NeighborSegment.Header.Tuner.TLabel", font=getStyleFontFromTkFont(font_tiny_bold), foreground="#ffff00")
    style.configure("K.Header.Tuner.TButton", font=getStyleFontFromTkFont(font_very_huge_bold))
    style.map("K.Header.Tuner.TButton", foreground=[('disabled', "#000000"), ('!disabled', "#bbbbbb")])
    style.configure("Auto.Mode.Header.Tuner.TLabel", font=getStyleFontFromTkFont(font_small_bold), background="#9ec113", foreground="#000000")
    style.configure("Manual.Mode.Header.Tuner.TLabel", font=getStyleFontFromTkFont(font_small_bold), background="#ff0000", foreground="#000000")
    style.map("Adjust.Tuner.TButton", foreground=[('disabled', "#000000"), ('!disabled', "#bbbbbb")])
    style.configure("NotTuned.Tuner.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Setting.Tuner.TLabel")
    style.configure("Button.Tuner.TLabel", background="#ac6c17")
    style.configure("Small.Button.Tuner.TLabel", font=getStyleFontFromTkFont(font_medium_bold))
    style.configure("Big.Button.Tuner.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Highlight.Big.Button.Tuner.TLabel", background="#d2923d")
    style.configure("VersionAndCopyright.TLabel", font=getStyleFontFromTkFont(font_very_tiny))
    style.configure("OperatingButton.TLabel", foreground="#ffff00")
    style.configure("Red.OperatingButton.TLabel", foreground="#ff0000")

    side = 150
    img = Image.open("resources/button_red.ico")
    global largeStandbyImg
    largeStandbyImg = ImageTk.PhotoImage(img.resize((200, 200), Image.ANTIALIAS))
    img = img.resize((side, side), Image.ANTIALIAS)
    global standbyImg
    standbyImg = ImageTk.PhotoImage(img)
    img = Image.open("resources/button_green.ico")
    global largeOperateImg
    largeOperateImg = ImageTk.PhotoImage(img.resize((200, 200), Image.ANTIALIAS))
    img = img.resize((side, side), Image.ANTIALIAS)
    global operateImg
    operateImg = ImageTk.PhotoImage(img)
    style.configure("Standby.OperatingButton.TLabel", image=standbyImg, foreground="#ff0000")
    style.configure("Operate.OperatingButton.TLabel", image=operateImg, foreground="#00ff00")
    style.configure("Standby.Large.OperatingButton.TLabel", image=largeStandbyImg, foreground="#ff0000")
    style.configure("Operate.Large.OperatingButton.TLabel", image=largeOperateImg, foreground="#00ff00")
    # Tunemode Disabled Img
    img = Image.open("resources/button_indigo_pressed.ico")
    img = img.resize((side, side), Image.ANTIALIAS)
    global tunemodeDisabledImg
    tunemodeDisabledImg = ImageTk.PhotoImage(img)
    # Tunemode Off Img
    img = Image.open("resources/button_blue_pressed.ico")
    img = img.resize((side, side), Image.ANTIALIAS)
    global tunemodeOffImg
    tunemodeOffImg = ImageTk.PhotoImage(img)
    # Tunemode On Img
    img = Image.open("resources/button_blue_hover.ico")
    img = img.resize((side, side), Image.ANTIALIAS)
    global tunemodeOnImg
    tunemodeOnImg = ImageTk.PhotoImage(img)
    style.configure("Disabled.Tunemode.OperatingButton.TLabel", image=tunemodeDisabledImg)
    style.configure("Off.Tunemode.OperatingButton.TLabel", image=tunemodeOffImg)
    style.configure("On.Tunemode.OperatingButton.TLabel", image=tunemodeOnImg)
    side = 65
    # Reset On Img
    img = Image.open("resources/button_green_hover.ico")
    global largeResetOnImg
    largeResetOnImg = ImageTk.PhotoImage(img.resize((200, 200), Image.ANTIALIAS))
    img = img.resize((side, side), Image.ANTIALIAS)
    global resetOnImg
    resetOnImg = ImageTk.PhotoImage(img)
    # Reset Off Img
    img = Image.open("resources/button_green_pressed.ico")
    global largeResetOffImg
    largeResetOffImg = ImageTk.PhotoImage(img.resize((200, 200), Image.ANTIALIAS))
    img = img.resize((side, side), Image.ANTIALIAS)
    global resetOffImg
    resetOffImg = ImageTk.PhotoImage(img)
    # Reset Error Img
    img = Image.open("resources/button_red.ico")
    global largeResetErrorImg
    largeResetErrorImg = ImageTk.PhotoImage(img.resize((200, 200), Image.ANTIALIAS))
    img = img.resize((side, side), Image.ANTIALIAS)
    global resetErrorImg
    resetErrorImg = ImageTk.PhotoImage(img)
    style.configure("Off.Reset.OperatingButton.TLabel", image=resetOffImg)
    style.configure("On.Reset.OperatingButton.TLabel", image=resetOnImg)
    style.configure("Off.Reset.Large.OperatingButton.TLabel", image=largeResetOffImg)
    style.configure("On.Reset.Large.OperatingButton.TLabel", image=largeResetOnImg)
    style.map("Reset.OperatingButton.TLabel", image=[('alternate', resetErrorImg)])
    style.map("Reset.Large.OperatingButton.TLabel", image=[('alternate', largeResetErrorImg)])

    # Menu

    # radio button
    img = Image.open("resources/radiobutton_empty.png")
    global radiobuttonEmpty
    radiobuttonEmpty = ImageTk.PhotoImage(img)
    img = Image.open("resources/radiobutton_selected.png")
    global radiobuttonSelected
    radiobuttonSelected = ImageTk.PhotoImage(img)

    global blueRadiobuttonEmpty
    img = Image.open("resources/radiobutton_empty_#344b98.png")
    blueRadiobuttonEmpty = ImageTk.PhotoImage(img)
    global blueRadiobuttonSelected
    img = Image.open("resources/radiobutton_selected_#344b98.png")
    blueRadiobuttonSelected = ImageTk.PhotoImage(img)

    # checkbox
    img = Image.open("resources/checkbox_empty.png")
    global checkboxEmpty
    checkboxEmpty = ImageTk.PhotoImage(img)
    img = Image.open("resources/checkbox_selected.png")
    global checkboxSelected
    checkboxSelected = ImageTk.PhotoImage(img)

    # up, top
    img = Image.open("resources/up.png")
    global upIcon
    global downIcon
    upIcon = ImageTk.PhotoImage(img)
    downIcon = ImageTk.PhotoImage(img.rotate(180))
    img = Image.open("resources/top.png")
    global topIcon
    global bottomIcon
    topIcon = ImageTk.PhotoImage(img)
    bottomIcon = ImageTk.PhotoImage(img.rotate(180))


    img = Image.open("resources/trash_32.png")
    global trashIcon
    trashIcon = ImageTk.PhotoImage(img)
    style.theme_create("menu", parent="clam")
    style.theme_use("menu")
    # Set the default colors
    style.configure("TLabel", background=defaultBgColor)
    style.configure("TFrame", background=defaultBgColor)
    style.configure("TButton", background=defaultBgColor)
    style.configure("TCheckbutton", background=defaultBgColor)
    style.configure("TNotebook", background=defaultBgColor)

    style.configure("Separator.TFrame", background="#888888")

    style.configure("Keyboard.TLabel", borderwidth=1, relief="groove", font=getStyleFontFromTkFont(font_very_huge))

    style.configure("TLabel", font=getStyleFontFromTkFont(font_small_bold))
    style.configure("Error.TLabel",  foreground="#ff0000")
    style.configure("VeryHuge.TLabel", font=getStyleFontFromTkFont(font_very_huge))
    style.map("Disableble.VeryHuge.TLabel", foreground=[("disabled", "#888888")])
    style.configure("Antenna.TLabel", foreground="#344b98")
    style.configure("AntennaCount.TLabel", font=getStyleFontFromTkFont(font_huge_bold), foreground="#344b98")
    style.configure("TButton", font=getStyleFontFromTkFont(font_small_bold))
    style.configure("AntennaCount.TButton", font=getStyleFontFromTkFont(font_huge_bold))
    style.configure("Settings.TButton", borderwidth=5, relief="groove", anchor="CENTER")
    style.map("Settings.TButton", foreground=[("disabled", "#888888"), ("", "#344b98")])
    style.map("Responding.Settings.TButton", background=[("alternate", "#BED998")])
    style.map("OnOff.Settings.TButton", foreground=[("alternate", "#ff0000"), ("disabled", "#ff0000"), ("", "#00ff00")])  # TODO remove red color for disabled
    style.configure("Trash.Settings.TButton", image=trashIcon, padding=5)
    style.configure("TNotebook", tabmargins=(20, 5, 20, 0))
    style.configure("TNotebook.Tab", font=getStyleFontFromTkFont(font_medium_bold), padding=(20, 5))

    # Poti Configuration
    style.configure("Poti.TFrame", background="#4444ff", borderwidth=5, relief="groove")
    style.configure("Value.Poti.TLabel", font=getStyleFontFromTkFont(font_very_huge_bold), background="#4444ff", foreground="#ffffff")
    style.configure("Label.Poti.TLabel", background="#4444ff", foreground="#ffffff")

    # Offset Calibration
    style.configure("Calibration.TFrame", borderwidth=5, relief="groove")
    style.configure("Sub.Calibration.TFrame", borderwidth=0, relief="flat")
    style.map("Calibration.TFrame", background=[("disabled", "#cccccc"), ("", "#ffffff")],)
    style.configure("ColumnHeader.Calibration.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Value.Calibration.TLabel", font=getStyleFontFromTkFont(font_very_huge_bold))
    style.map("Value.Calibration.TLabel",
              background=[("disabled", "#cccccc"), ("", "#ffffff")],
              foreground=[("disabled", "#888888"), ("", "#000000")])
    style.configure("Label.Calibration.TLabel")
    style.map("Label.Calibration.TLabel",
              background=[("disabled", "#cccccc"), ("", "#ffffff")],
              foreground=[("disabled", "#888888"), ("", "#000000")])
    style.configure("Calibration.TButton", font=getStyleFontFromTkFont(font_huge_bold))
    style.map("Calibration.TButton",
              background=[("disabled", "#cccccc")],
              foreground=[("disabled", "#888888"), ("", "#000000")])
    style.configure("Label.ValueDisplay.Calibration.TLabel", font=getStyleFontFromTkFont(font_large_bold))
    style.configure("Value.ValueDisplay.Calibration.TLabel", font=getStyleFontFromTkFont(font_large_bold))

    # VNC
    style.configure("IP.TLabel", foreground="#666666")

    # Update
    style.configure("VersionType.Update.TLabel", font=getStyleFontFromTkFont(font_very_huge_bold))

    # Interface
    style.configure('TRadiobutton', font=getStyleFontFromTkFont(font_very_huge), indicatorsize=0)
    style.map('TRadiobutton', foreground=[('disabled', "#888888")],
              image=[("selected", radiobuttonSelected), ("", radiobuttonEmpty)])


    style.configure('TCheckbutton', font=getStyleFontFromTkFont(font_very_huge), indicatorsize=0)
    style.map('TCheckbutton', foreground=[('disabled', "#888888")],
              image=[("selected", checkboxSelected), ("", checkboxEmpty)])

    style.map('Radiobuttonlike.TCheckbutton', image=[("selected", radiobuttonSelected), ("", radiobuttonEmpty)])
    style.map('Antenna.Radiobuttonlike.TCheckbutton', image=[("selected", blueRadiobuttonSelected), ("", blueRadiobuttonEmpty)])

    style.configure('Small.TRadiobutton', font=getStyleFontFromTkFont(font_large))
    style.configure('Small.TCheckbutton', font=getStyleFontFromTkFont(font_large))

    default_combo_foreground = style.lookup("TCombobox", "foreground")
    style.configure("TCombobox", font=getStyleFontFromTkFont(font_very_huge), background=defaultBgColor,
                    selectbackground=defaultBgColor,
                    fieldbackground=defaultBgColor, arrowsize=60, padding=5, arrowcolor='green')
    style.map("TCombobox", selectforeground=[('!disabled', default_combo_foreground), ('disabled', 'grey')],
                    foreground=[('!disabled', default_combo_foreground), ('disabled', 'grey')],
              arrowcolor=[('!disabled', 'black'), ('disabled', 'grey')])
    app.option_add("*TCombobox*Listbox.font", getStyleFontFromTkFont(font_very_huge))
    app.option_add("*TCombobox.font", getStyleFontFromTkFont(font_very_huge))
    app.option_add("*TCombobox*Listbox.background", defaultBgColor)
    style.configure('Vertical.TScrollbar', width=60)
    style.configure('Vertical.TScrollbar', arrowsize=60)
    style.configure('Status.TEntry', fieldbackground=defaultBgColor, padding=5)
    style.map('Status.TEntry', foreground=[('invalid', 'red'), ('!invalid', 'green')])

    style.configure('Config.TEntry', padding=5)
    style.map('Validated.Config.TEntry', foreground=[('invalid', 'red'), ('!invalid', 'green')])

    style.map('ValidationError.TLabel', foreground=[('!alternate', 'red'), ('alternate', defaultBgColor)])

    style.configure('WithoutArrows.TSpinbox', arrowsize=0, padding=5)
    style.configure('WithoutArrowsSpinboxArrow.Settings.TButton', font=getStyleFontFromTkFont(font_large_bold), padding=(15, 0))
    style.map("WithoutArrowsSpinboxArrow.Settings.TButton", foreground=[("!disabled", "#000000")])

    style.configure('Top.Settings.TButton', image=topIcon)
    style.configure('Up.Settings.TButton', image=upIcon)
    style.configure('Down.Settings.TButton', image=downIcon)
    style.configure('Bottom.Settings.TButton', image=bottomIcon)

def useDarkTheme():
    global style
    style.theme_use("custom_dark")


def useMenuTheme():
    global style
    style.theme_use("menu")

def getCurrentTheme():
    global style
    return style.theme_use()

def useTheme(theme):
    global style
    style.theme_use(theme)
