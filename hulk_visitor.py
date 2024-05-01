from abc import ABC, abstractmethod

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class Visitor(ABC):
    @abstractmethod
    def visitLiteral(self, lit):
        pass

    @abstractmethod
    def visitGrouping(self, group):
        pass

    @abstractmethod
    def visitUnary(self, unary):
        pass

    @abstractmethod
    def visitBinary(self, binary):
        pass

class AstPrinter(Visitor):
    def visitLiteral(self, lit):
        return lit.literal.lexeme
    def visitGrouping(self, group):
        return "(group " + group.inside.accept(self) +  ")"
    def visitUnary(self, unary):
        return "(" + unary.operator.lexeme + " " + unary.exp.accept(self) + ")"
    def visitBinary(self, binary):
        return "(" + binary.left.accept(self) + " " + binary.operator.lexeme   +   " " + binary.right.accept(self) + ")"

class Literal(Expr):
    def __init__(self, token):
        self.literal = token

    def accept(self, visitor):
        return visitor.visitLiteral(self)

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