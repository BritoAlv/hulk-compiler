from abc import ABC, abstractmethod

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