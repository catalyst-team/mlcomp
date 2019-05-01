from enum import Enum
from mlcomp.utils.misc import to_snake

class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    @classmethod
    def names(cls):
        return [e.name for e in cls]

    @classmethod
    def names_snake(cls):
        return [to_snake(n) for n in cls.names()]


class TaskStatus(OrderedEnum):
    NotRan = 0
    Queued = 1
    InProgress = 2
    Failed = 3
    Stopped = 4
    Skipped = 5
    Success = 6


class TaskType(OrderedEnum):
    Train = 0
    Infer = 1
    User = 2


class StepStatus(OrderedEnum):
    InProgress = 0
    Failed = 1
    Stopped = 2
    Successed = 3
