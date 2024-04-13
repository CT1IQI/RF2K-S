from enum import Enum


class DebugCalibrationType(Enum):
    BIAS = 0
    INPUT = 1
    INPUT_OFFSET = 2


class Band(Enum):
    BAND_6_M = (0, '6m')
    BAND_10_M = (1, '10m')
    BAND_12_M = (2, '12m')
    BAND_15_M = (3, '15m')
    BAND_17_M = (4, '17m')
    BAND_20_M = (5, '20m')
    BAND_30_M = (6, '30m')
    BAND_40_M = (7, '40m')
    BAND_60_M = (8, '60m')
    BAND_80_M = (9, '80m')
    BAND_160_M = (10, '160m')

    def __init__(self, value, displayName):
        self.enumValue = value
        self.displayName = displayName
