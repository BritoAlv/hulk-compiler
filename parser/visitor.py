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

    @abstractmethod
    def visitTernary(self, ternary):
        pass


class AstPrinter(Visitor):
    def visitLiteral(self, lit):
        return lit.literal.lexeme

    def visitGrouping(self, group):
        return "(" + group.inside.accept(self) + ")"

    def visitUnary(self, unary):
        return unary.operator.lexeme + "(" + unary.exp.accept(self) + ")"

    def visitBinary(self, binary):
        return (
            binary.operator.lexeme
            + "("
            + binary.left.accept(self)
            + " "
            + binary.right.accept(self)
            + ")"
        )

    def visitTernary(self, ternary):
        return (
            "["
            + ternary.op1.lexeme
            + " "
            + ternary.left.accept(self)
            + " "
            + ternary.middle.accept(self)
            + " "
            + ternary.op2.lexeme
            + " "
            + ternary.right.accept(self)
            + "]"
        )


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
        self.current += self.do_space() + lit.literal.lexeme + "\n"
        return self.current

    def visitGrouping(self, group):
        self.current += self.do_space() + "(" + "\n"
        self.indent += 1
        group.inside.accept(self)
        self.indent -= 1
        self.current += self.do_space() + ")" + "\n"
        return self.current

    def visitUnary(self, unary):
        self.current += self.do_space() + unary.operator.lexeme + "\n"
        self.indent += 1
        unary.exp.accept(self)
        self.indent -= 1
        return self.current

    def visitBinary(self, binary):
        self.current += self.do_space() + binary.operator.lexeme + "\n"
        self.indent += 1
        binary.left.accept(self)
        binary.right.accept(self)
        self.indent -= 1
        return self.current

    def visitTernary(self, ternary):
        self.current += self.do_space() + ternary.op1.lexeme + "\n"
        self.indent += 1
        ternary.left.accept(self)
        self.indent -= 1
        self.current += self.do_space() + ternary.op2.lexeme + "\n"
        self.indent += 1
        ternary.middle.accept(self)
        ternary.right.accept(self)
        self.indent -= 1 
        return self.current

class AstEvaluator(Visitor):
    def visitLiteral(self, lit):
        return lit.literal.literal

    def visitGrouping(self, group):
        return group.inside.accept(self)

    def visitUnary(self, unary):
        value = unary.exp.accept(self)
        match unary.operator.tokenType:
            case TokenType.MINUS:
                return -value
            case TokenType.NOT:
                if value == 0:
                    return 1
                else:
                    return 0
            case _:
                raise Exception("How evaluates unary operator: ")

    def visitTernary(self, ternary):
        if ternary.op1.tokenType == TokenType.TERNARY_COND and ternary.op2.tokenType == TokenType.TERNARY_SEP:
            if ternary.left.accept(self) != 0:
                return ternary.middle.accept(self)
            else:
                return ternary.right.accept(self)
        else:
            raise Exception("This ternary combination is not implemented")

    def visitBinary(self, binary):
        left = binary.left.accept(self)
        right = binary.right.accept(self)
        match binary.operator.tokenType:
            case TokenType.PLUS:
                return left + right
            case TokenType.MINUS:
                return left - right
            case TokenType.MULT:
                return left * right
            case TokenType.DIV:
                return left // right
            case TokenType.EXP:
                return left**right
            case TokenType.XOR:
                return left ^ right
            case TokenType.AND:
                return left and right
            case TokenType.OR:
                return left or right
            case TokenType.NAND:
                return not (left and right)
            case TokenType.GREATER:
                if left > right:
                    return 1
                return 0
            case TokenType.GREATER_EQUAL:
                if left >= right:
                    return 1
                return 0
            case TokenType.LESS:
                if left < right:
                    return 1
                return 0
            case TokenType.LESS_EQUAL:
                if left <= right:
                    return 1
                return 0
            case TokenType.EQUAL:
                if left == right:
                    return 1
                return 0
            case TokenType.NOT_EQUAL:
                if left != right:
                    return 1
                return 0

            case TokenType.SHIFT_LEFT:
                return left << right

            case TokenType.SHIFT_RIGHT:
                return left >> right

            case _:
                raise Exception(
                    "How evaluates binary operator: "
                    + binary.operator.tokentype.toString(False)
                )