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

class Variable(Expr):
    def __init__(self, token):
        self.id = token
    def accept(self, visitor):
        return visitor.visitVariable(self)

class Grouping(Expr):
    def __init__(self, open, inside, closed):
        self.open = open
        self.inside = inside
        self.closed = closed

    def accept(self, visitor):
        return visitor.visitGrouping(self)

class UnaryExpr(Expr):
    def __init__(self, op, exp):
        self.operator = op
        self.exp = exp

    def accept(self, visitor):
        return visitor.visitUnary(self)

class BinaryExpr(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.operator = op
        self.right = right

    def accept(self, visitor):
        return visitor.visitBinary(self)

class TernaryExpr(Expr):
    def __init__(self, left, op1, middle, op2, right):
        self.left = left
        self.op1 = op1
        self.middle = middle
        self.op2 = op2
        self.right = right
    def accept(self, visitor):
        return visitor.visitTernary(self)