from lexer.lexer import *
from parser.visitor import *
from parser.expressions import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def valid(self):
        return self.current < len(self.tokens)

    def current_tokenType(self):
        return self.tokens[self.current].tokenType

    def parseLiteral(self):
        if self.valid():
            if self.current_tokenType() == TokenType.LPAREN:
                lp = self.tokens[self.current]
                self.current += 1
                part = self.parseExpr()
                if (not self.valid()) or self.tokens[
                    self.current
                ].tokenType != TokenType.RPAREN:
                    raise Exception("No ) found for " + lp.toString(False))
                rp = self.tokens[self.current]
                self.current += 1
                return Grouping(lp, part, rp)
            else:
                if self.current_tokenType() == TokenType.NUMBER:
                    literal = self.tokens[self.current]
                    self.current += 1
                    return Literal(literal)
                raise Exception(
                    "Expected Literal got : " + self.tokens[self.current].toString(True)
                )
        else:
            raise Exception("Invalid syntax")

    def parsePrimary(self):
        result = self.parseLiteral()
        if self.valid() and self.current_tokenType() in [TokenType.EXP]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parsePrimary()
            result = BinaryExpr(result, op, part2)
        return result

    def parseFactor(self):
        if self.valid():
            if self.current_tokenType() in [TokenType.MINUS, TokenType.NOT]:
                op = self.tokens[self.current]
                self.current += 1
                part = self.parseExpr()
                return UnaryExpr(op, part)
            else:
                return self.parsePrimary()
        else:
            raise Exception("Invalid syntax")

    def parseTerm(self):
        result = self.parseFactor()
        while self.valid() and self.current_tokenType() in [
            TokenType.MULT,
            TokenType.DIV,
            TokenType.AND,
            TokenType.NAND,
        ]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseFactor()
            result = BinaryExpr(result, op, part2)
        return result

    def parseExpr(self):
        result = self.parseTerm()
        while self.valid() and self.current_tokenType() in [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.SHIFT_LEFT,
            TokenType.SHIFT_RIGHT,
            TokenType.OR,
            TokenType.XOR,
        ]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseTerm()
            result = BinaryExpr(result, op, part2)
        return result

    def parseEq(self):
        result = self.parseExpr()
        if self.valid() and self.current_tokenType() in [
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL
        ]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseEq()
            result = BinaryExpr(result, op, part2)
        return result

    def parse(self):
        expr = self.parseEq()
        if self.current != len(self.tokens):
            raise Exception("invalid syntax")
        return expr
