from abc import ABC, abstractmethod
from textwrap import indent

from lexer.lexer import TokenType

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
        return "(" + group.inside.accept(self) +  ")"
    def visitUnary(self, unary):
        return  unary.operator.lexeme + "(" + unary.exp.accept(self) + ")"
    def visitBinary(self, binary):
        return binary.operator.lexeme  + "(" + binary.left.accept(self) + " " + binary.right.accept(self) + ")"

class TreePrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.current = ""

    def do_space(self):
        a = ""
        for i in range(0, self.indent):
            a += "    "
        return a + "└── "

    def visitLiteral(self, lit):
        self.current += self.do_space()  + lit.literal.lexeme + "\n"
        return self.current

    def visitGrouping(self, group):
        self.current += self.do_space()  + "(" + "\n"
        self.indent += 1
        group.inside.accept(self)
        self.indent -= 1
        self.current += self.do_space()  +  ")" + "\n"
        return self.current

    def visitUnary(self, unary):
        self.current += self.do_space()  + unary.operator.lexeme + "\n"
        self.indent += 1
        unary.exp.accept(self)
        self.indent -= 1
        return  self.current

    def visitBinary(self, binary):
        self.current += self.do_space()  + binary.operator.lexeme + "\n"
        self.indent += 1
        binary.left.accept(self)
        binary.right.accept(self)
        self.indent -= 1
        return self.current

class AstEvaluator(Visitor):
    def visitLiteral(self, lit):
        return lit.literal.literal
    def visitGrouping(self, group):
        return group.inside.accept(self)
    def visitUnary(self, unary):
        value = unary.exp.accept(self)
        if unary.operator.tokenType == TokenType.MINUS:
            return -value
        else:
            return value
    def visitBinary(self, binary):
        left = binary.left.accept(self)
        right = binary.right.accept(self)
        if binary.operator.tokenType == TokenType.PLUS:
            return left + right
        elif binary.operator.tokenType == TokenType.MINUS:
            return left - right
        elif binary.operator.tokenType == TokenType.MULT:
            return left * right
        elif binary.operator.tokenType == TokenType.DIV:
            return left // right
        elif binary.operator.tokenType == TokenType.EXP:
            return left ** right
        elif binary.operator.tokenType == TokenType.XOR:
            return left ^ right