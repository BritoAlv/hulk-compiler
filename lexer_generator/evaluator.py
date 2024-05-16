from abc import ABC, abstractmethod

from const import *
from regular_expressions import *
from finite_automata import *
from lexer_generator import *


class VisitorExp(ABC):
    @abstractmethod
    def visitUnion(self, expr):
        pass

    @abstractmethod
    def visitUnary(self, expr):
        pass

    @abstractmethod
    def visitLiteral(self, expr):
        pass

    @abstractmethod
    def visitParen(self, expr):
        pass


class Evaluator(VisitorExp):
    def __init__(self):
        pass

    def visitUnion(self, expr: BinaryExpression) -> NFA:
        assert expr.op in [UNION, CONCATENATE]
        A = expr.left.accept(self)
        B = expr.right.accept(self)
        if expr.op == UNION:
            return UnionNFA(A, B)
        return ConcatenateNFA(A, B)

    def visitUnary(self, expr: UnaryExpression) -> NFA:
        A = expr.left.accept(self)
        if expr.op == STAR:
            return Star(A)
        return Question(A)

    def visitLiteral(self, expr: LiteralExpression) -> NFA:
        return NFAfor_char(expr.literal)

    def visitParen(self, expr: ParenExpression) -> NFA:
        return expr.expr.accept(self)


class Printer:
    def __init__(self):
        pass

    def visitUnion(self, expr: BinaryExpression) -> str:
        assert expr.op in [UNION, CONCATENATE]
        A = expr.left.accept(self)
        B = expr.right.accept(self)
        return expr.op + " [" + A + ", " + B + "]"

    def visitUnary(self, expr: UnaryExpression) -> str:
        A = expr.left.accept(self)
        return expr.op + " " + "[" + A + "]"

    def visitLiteral(self, expr: LiteralExpression) -> str:
        return expr.literal

    def visitParen(self, expr) -> str:
        return "(" + expr.expr.accept(self) + ")"


front = ParenExpression(
    "(", BinaryExpression(LiteralExpression("a"), UNION, LiteralExpression("b")), ")"
)

end = ParenExpression(
    "(",
    BinaryExpression(
        LiteralExpression("a"),
        UNION,
        BinaryExpression(LiteralExpression("b"), UNION, LiteralExpression("1")),
    ),
    ")",
)

unary = UnaryExpression(end, STAR)

exp = BinaryExpression(front, CONCATENATE, unary)


printer = Printer()
print(exp.accept(printer))
eval = Evaluator()
M = UnaryExpression(exp, STAR).accept(eval)
D = M.ConvertNFA_DFA()
print(D.simulate("aab1aabba"))
print(D.simulate("1aab"))
print(D.simulate("1ab1"))