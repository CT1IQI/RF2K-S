from enum import Enum


class Generation(Enum):

    RF2K_PLUS = 0
    RF2K_S = 1

    def __str__(self):
        if self == self.RF2K_PLUS:
            return "B26 RF2K+"
        if self == self.RF2K_S:
            return "B26 RF2K-S"
        return ""