from abc import ABC, abstractmethod

from common.constants import *
from lexing.lexer_generator.operations import ConcatenateNFA, NFAfor_char, Question, Star, UnionNFA
from lexing.lexer_generator.regular_expressions import *
from lexing.lexer_generator.finite_automata import *

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