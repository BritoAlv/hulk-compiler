from abc import ABC, abstractmethod


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class Literal(Expr):
    def __init__(self, token):
        self.literal = token

    def accept(self, visitor):
        return visitor.visitLiteral(self)

class BinaryExpr(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.operator = op
        self.right = right

    def accept(self, visitor):
        return visitor.visitBinary(self)