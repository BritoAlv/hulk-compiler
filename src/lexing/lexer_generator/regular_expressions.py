from abc import ABC, abstractmethod
from lexing.lexer_generator.const import CONCATENATE, QUESTION, STAR, UNION

class RegularExpression(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class BinaryExpression(RegularExpression):
    def __init__(self, left : RegularExpression, op : str, right : RegularExpression):
        assert(op in [CONCATENATE, UNION])
        self.left = left
        self.op = op
        self.right = right
    
    def accept(self, visitor):
        return visitor.visitUnion(self)
    
class UnaryExpression(RegularExpression):
    def __init__(self, left : RegularExpression, op : str):
        assert(op in [STAR, QUESTION])
        self.left = left
        self.op = op
    
    def accept(self, visitor):
        return visitor.visitUnary(self)

class LiteralExpression(RegularExpression):
    def __init__(self, literal : str):
        self.literal = literal
    
    def accept(self, visitor):
        return visitor.visitLiteral(self)
    
class ParenExpression(RegularExpression):
    def __init__(self, openP : str, expr: RegularExpression, closedP : str):
        assert(openP == "(")
        assert(closedP == ")")
        self.openP = openP
        self.expr = expr
        self.closedP = expr

    def accept(self, visitor):
        return visitor.visitParen(self)