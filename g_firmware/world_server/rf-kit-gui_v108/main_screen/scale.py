from abc import ABC, abstractmethod
from math import cos, pi, sin, log
from tkinter import ttk, Canvas, PhotoImage, StringVar

from PIL import ImageTk, Image

from data import Data
from dimensions import DIMENSIONS


class Scale(ABC, ttk.Frame):

    def __init__(self, container, scale_click_callback=None):
        super().__init__(container, height=DIMENSIONS.SCALE_HEIGHT)
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0, bg="#000000")
        self.canvas.grid(sticky="wnes")
        if scale_click_callback is not None:
            self.canvas.bind('<ButtonRelease-1>', lambda _: scale_click_callback())

    @abstractmethod
    def update_scale(self):
        pass


class NeedleScale(Scale):
    circleRadius = 390
    coveredDegrees = 60  # The Scale covers 60° of the full circle
    forwardStartPoint = (429, 428)
    reflectedStartPoint = (129, 431)
    scaleFactors = [10, 1, 100]  # 0: Standby, 1: Operate, 2: Tune

    def __init__(self, container, scale_click_callback):
        super().__init__(container, scale_click_callback)
        self.images = None
        self.activeScaleIndex = 0
        self.curImage = None
        self.activeScaleFactor = self.scaleFactors[self.activeScaleIndex]
        self.backgroundImage = None

        self.fpercentage = 0
        self.rpercentage = 0

    def drawScaleAndNeedles(self):
        # Call update_idletasks to make all geometry changes active so that winfo_width/height return correct values
        self.update_idletasks()

        images = [Image.open("resources/kreuzzeiger_standby.png"), Image.open("resources/kreuzzeiger_operate.png"),
                  Image.open("resources/kreuzzeiger_tuner.png")]
        self.images = [
            ImageTk.PhotoImage(image.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.ANTIALIAS))
            for image in images]
        self.curImage = self.images[self.activeScaleIndex]
        self.backgroundImage = self.canvas.create_image(0, 0, image=self.curImage, anchor="nw")

        self.drawNeedles()

    def calculateForwardCoordinates(self, percentage):
        if percentage < 0:
            percentage = 0
        elif percentage > 1:
            percentage = 1
        nullPointAngle = 20.2
        x = 429 - (self.circleRadius * cos(2 * pi * ((nullPointAngle + self.coveredDegrees * percentage) / 360)))
        y = 428 - (self.circleRadius * sin(2 * pi * ((nullPointAngle + self.coveredDegrees * percentage) / 360)))
        return x, y

    def calculateReflectedCoordinates(self, percentage):
        if percentage < 0:
            percentage = 0
        elif percentage > 1:
            percentage = 1
        nullPointAngle = 21.3
        x = 129 + (self.circleRadius * cos(2 * pi * ((nullPointAngle + self.coveredDegrees * percentage) / 360)))
        y = 431 - (self.circleRadius * sin(2 * pi * ((nullPointAngle + self.coveredDegrees * percentage) / 360)))
        return x, y

    def drawNeedles(self):
        needleOptions = {"width": 2, "fill": "red"}
        self.forwardNeedle = self.canvas.create_line(*self.forwardStartPoint,
                                                     self.calculateForwardCoordinates(self.fpercentage),
                                                     needleOptions)
        self.reflectNeedle = self.canvas.create_line(*self.reflectedStartPoint,
                                                     self.calculateReflectedCoordinates(self.rpercentage),
                                                     needleOptions)

    def update_scale(self):
        # Switch to the correct scale
        self.switchToScale(
            1 if Data.getInstance().inOperate else 2 if Data.getInstance().tunerState == Data.TunerState.MANUAL and Data.getInstance().P_F <= 30 else 0)
        forward_linear_limit = 200 / self.activeScaleFactor
        backward_linear_limit = 100 / self.activeScaleFactor
        # Update the needles
        if Data.getInstance().P_F < forward_linear_limit:  # linear approximation from zero
            self.fpercentage = self.forward_log(forward_linear_limit) * Data.getInstance().P_F / forward_linear_limit
        else:
            self.fpercentage = self.forward_log(Data.getInstance().P_F)
        if Data.getInstance().P_R < backward_linear_limit / self.activeScaleFactor:  # linear approximation from zero
            self.rpercentage = self.reflected_log(
                backward_linear_limit) * Data.getInstance().P_R / backward_linear_limit
        else:
            self.rpercentage = self.reflected_log(Data.getInstance().P_R)
        forwardCoordinates = self.calculateForwardCoordinates(self.fpercentage)
        self.canvas.coords(self.forwardNeedle, *self.forwardStartPoint, *forwardCoordinates)
        reflectedCoordinates = self.calculateReflectedCoordinates(self.rpercentage)
        self.canvas.coords(self.reflectNeedle, *self.reflectedStartPoint, *reflectedCoordinates)

    def forward_log(self, f):
        multiplied_f = f * self.activeScaleFactor
        return log(multiplied_f / 1000) * 0.27979 + 0.6933

    def reflected_log(self, r):
        multiplied_r = r * self.activeScaleFactor
        return log(multiplied_r) * 0.33525 - 1.3189

    def switchToScale(self, index):
        if index == self.activeScaleIndex:
            return
        self.activeScaleIndex = index
        self.activeScaleFactor = self.scaleFactors[index]
        self.canvas.itemconfig(self.backgroundImage, image=self.images[self.activeScaleIndex])
        self.update_scale()


class BarScale(Scale):
    FORWARD_ONLY_PERCENTAGE = 0.35

    class ScaleData:
        maxForward: int
        maxReflected: int
        imageName: str
        image: PhotoImage
        only_forward_image: PhotoImage

        def __init__(self, maxForward, maxReflected, imageName):
            self.maxForward = maxForward
            self.maxReflected = maxReflected
            self.imageName = imageName

        def create_image(self, width, height):
            img = Image.open(self.imageName)
            img = img.resize((width, height), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(img)

        def create_only_forward_image(self, width, height):
            img = Image.open(self.imageName)
            img = img.resize((width, int(height // BarScale.FORWARD_ONLY_PERCENTAGE)), Image.ANTIALIAS)
            img = img.crop((0,0,width,height))  #left, upper, right, and lower
            self.only_forward_image = ImageTk.PhotoImage(img)


    scaleData = [ScaleData(200, 25, "resources/balken1.png"),  # 0: Standby
                 ScaleData(2000, 250, "resources/balken2.png")]  # 1: Operate


    def __init__(self, container, scale_click_callback=None, only_forward=False):
        super().__init__(container, scale_click_callback)
        self.onlyForward = only_forward

        self.scaleImageOnCanvas = None
        self.activeScaleIndex = 0
        self.activeScaleData = self.scaleData[self.activeScaleIndex]

        self.fpercentage = 0
        self.rpercentage = 0
        self.swrpercentage = 0

        self.width = None
        self.calculation_base_height = None

        self.barHeight = None
        self.maxIndicatorWidth = None
        self.fullBarWidth = None
        self.scaleStartX = None
        self.nullValueX = None
        self.forwardStartPoint = None
        self.reflectedStartPoint = None
        self.swrStartPoint = None

    def drawScaleAndBars(self):
        # Call update_idletasks to make all geometry changes active so that winfo_width/height return correct values
        self.update_idletasks()
        self.width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.calculation_base_height = int(height // BarScale.FORWARD_ONLY_PERCENTAGE) if self.onlyForward else height

        self.barHeight = (31 * self.calculation_base_height) // 480
        self.maxIndicatorWidth = (8 * self.width) // 700
        self.fullBarWidth = (651 * self.width) // 700
        self.scaleStartX = (20 * self.width) // 700
        self.nullValueX = self.scaleStartX + self.maxIndicatorWidth // 2
        self.forwardStartPoint = (self.scaleStartX, (62 * self.calculation_base_height) // 480)
        self.reflectedStartPoint = (self.scaleStartX,  (224 * self.calculation_base_height) // 480)
        self.swrStartPoint = (self.scaleStartX, (382 * self.calculation_base_height) // 480)

        # Create the images for the scales
        if self.onlyForward:
            [scaleData.create_only_forward_image(self.width, height) for scaleData in self.scaleData]
            self.scaleImageOnCanvas = self.canvas.create_image(0, 0, image=self.activeScaleData.only_forward_image, anchor="nw")
        else:
            [scaleData.create_image(self.width, height) for scaleData in self.scaleData]
            self.scaleImageOnCanvas = self.canvas.create_image(0, 0, image=self.activeScaleData.image, anchor="nw")


        self.drawBars()

    def calculateForwardCoordinates(self, percentage):
        if percentage < 0:
            percentage = 0
        elif percentage > 1:
            percentage = 1
        x = self.nullValueX + self.fullBarWidth * percentage
        y = self.forwardStartPoint[1] + self.barHeight
        return x, y

    def calculateReflectedCoordinates(self, percentage):
        if percentage < 0:
            percentage = 0
        elif percentage > 1:
            percentage = 1
        x = self.nullValueX + self.fullBarWidth * percentage
        y = self.reflectedStartPoint[1] + self.barHeight
        return x, y

    def calculateSWRCoordinates(self, percentage):
        if percentage < 0:
            percentage = 0
        elif percentage > 1:
            percentage = 1
        x = self.nullValueX + self.fullBarWidth * percentage
        y = self.swrStartPoint[1] + self.barHeight
        return x, y

    def calculateMaxIndicatorCoordinates(self, y1, percentage):
        if percentage < 0:
            percentage = 0
        elif percentage > 1:
            percentage = 1
        x1 = self.scaleStartX + self.fullBarWidth * percentage
        x2 = x1 + self.maxIndicatorWidth
        y2 = y1 + self.barHeight
        return x1, y1, x2, y2

    def drawBars(self):
        barOptions = {"fill": "#007aff"}
        self.forwardBar = self.canvas.create_rectangle(*self.forwardStartPoint,
                                                       *(self.calculateForwardCoordinates(self.fpercentage)),
                                                       barOptions)
        if not self.onlyForward:
            self.reflectedBar = self.canvas.create_rectangle(*self.reflectedStartPoint,
                                                             *(self.calculateReflectedCoordinates(self.rpercentage)),
                                                             barOptions)
            self.swrBar = self.canvas.create_rectangle(*self.swrStartPoint,
                                                       *(self.calculateSWRCoordinates(self.swrpercentage)))
        barOptions = {"fill": "yellow"}
        self.forwardMaxIndicator = self.canvas.create_rectangle(
            *self.calculateMaxIndicatorCoordinates(self.forwardStartPoint[1], 0),
            barOptions)
        if not self.onlyForward:
            self.reflectedMaxIndicator = self.canvas.create_rectangle(
                *self.calculateMaxIndicatorCoordinates(self.reflectedStartPoint[1], 0),
                barOptions)
            self.swrMaxIndicator = self.canvas.create_rectangle(
                *self.calculateMaxIndicatorCoordinates(self.swrStartPoint[1], 0),
                barOptions)
        style = "Huge.Scale.TLabel" if self.onlyForward else "Scale.TLabel"
        label = ttk.Label(self.canvas, text="Forward", style=style)
        self.canvas.create_window(((338 * self.width) // 700, (18 * self.calculation_base_height) // 480), window=label)
        if not self.onlyForward:
            label = ttk.Label(self.canvas, text="Reflected", style=style)
            self.canvas.create_window(((338 * self.width) // 700, (180 * self.calculation_base_height) // 480), window=label)
            label = ttk.Label(self.canvas, text="SWR", style=style)
            self.canvas.create_window(((338 * self.width) // 700, (337 * self.calculation_base_height) // 480), window=label)
        # Create the value labels
        label = ttk.Label(self.canvas, textvariable=Data.getInstance().vars.forwardValueVar, style="Value."+style)
        self.canvas.create_window(((689 * self.width) // 700, (142 * self.calculation_base_height) // 480), anchor="e", window=label)
        if not self.onlyForward:
            label = ttk.Label(self.canvas, textvariable=Data.getInstance().vars.reflectedValueVar, style="Value."+style)
            self.canvas.create_window(((689 * self.width) // 700, (304 * self.calculation_base_height) // 480), anchor="e", window=label)
            label = ttk.Label(self.canvas, textvariable=Data.getInstance().vars.swrValueVar, style="Value."+style)
            self.canvas.create_window(((689 * self.width) // 700, (460 * self.calculation_base_height) // 480), anchor="e", window=label)

    def calculateFPercentage(self, val):
        return val / self.activeScaleData.maxForward

    def calculateRPercentage(self, val):
        return val / self.activeScaleData.maxReflected

    def calculateSWRPercentage(self, val):
        if val < 1:
            return 0
        return min(log(val, 1.1575) / 13.1, 1)

    def updateSWRBarColorForCoords(self, coords):
        x = coords[0]
        if x >= (278 * self.width) // 700:
            color = "#d93919"
        elif x >= (162 * self.width) // 700:
            color = "#e48f12"
        else:
            color = "#9dc10b"
        self.canvas.itemconfig(self.swrBar, fill=color)

    def update_scale(self):
        # Switch to the correct scale
        self.switchToScale(1 if Data.getInstance().inOperate else 0)
        # Update the bars
        self.fpercentage = self.calculateFPercentage(Data.getInstance().P_F)
        if not self.onlyForward:
            self.rpercentage = self.calculateRPercentage(Data.getInstance().P_R)
            self.swrpercentage = self.calculateSWRPercentage(Data.getInstance().SWR)
        forwardCoordinates = self.calculateForwardCoordinates(self.fpercentage)
        self.canvas.coords(self.forwardBar, *self.forwardStartPoint, *forwardCoordinates)
        if not self.onlyForward:
            reflectedCoordinates = self.calculateReflectedCoordinates(self.rpercentage)
            self.canvas.coords(self.reflectedBar, *self.reflectedStartPoint, *reflectedCoordinates)
            swrCoordinates = self.calculateSWRCoordinates(self.swrpercentage)
            self.canvas.coords(self.swrBar, *self.swrStartPoint, *swrCoordinates)
        # Update the max indicators
        self.canvas.coords(self.forwardMaxIndicator,
                           *self.calculateMaxIndicatorCoordinates(self.forwardStartPoint[1],
                                                                  self.calculateFPercentage(
                                                                      Data.getInstance().max_P_F)))

        if not self.onlyForward:
            self.canvas.coords(self.reflectedMaxIndicator,
                               *self.calculateMaxIndicatorCoordinates(self.reflectedStartPoint[1],
                                                                      self.calculateRPercentage(
                                                                          Data.getInstance().max_P_R)))
            self.canvas.coords(self.swrMaxIndicator,
                               *self.calculateMaxIndicatorCoordinates(self.swrStartPoint[1],
                                                                      self.calculateSWRPercentage(
                                                                          Data.getInstance().max_SWR)))
            self.updateSWRBarColorForCoords(swrCoordinates)
        if self.onlyForward:
            self.canvas.itemconfig(self.scaleImageOnCanvas, image=self.activeScaleData.only_forward_image)
        else:
            self.canvas.itemconfig(self.scaleImageOnCanvas, image=self.activeScaleData.image)

    def switchToScale(self, index):
        if index == self.activeScaleIndex:
            return
        self.activeScaleIndex = index
        self.activeScaleData = self.scaleData[index]
        self.update_scale()
