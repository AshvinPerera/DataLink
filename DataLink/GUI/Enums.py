from enum import Enum, IntEnum


class State(Enum):
    NO_OPERATION = 1
    SOCKET_CREATION = 2


class SocketType(Enum):
    INPUT = 1
    OUTPUT = 2


class PropertyUI(IntEnum):
    NO_UI = 0
    IMPORT_CSV_UI = 1
