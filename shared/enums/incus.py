from enum import Enum


class VPSAction(Enum):
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'

    FREEZE = 'freeze'
    UNFREEZE = 'unfreeze'
