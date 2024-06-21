

from abc import ABC, abstractmethod

class Statement(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class Expr(Statement, ABC):
    pass
