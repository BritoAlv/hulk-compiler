from lexer.lexer import *
from parser.visitor import *
from parser.expressions import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def valid(self):
        return self.current < len(self.tokens)

    def parseLiteral(self):
        if self.valid():
            if self.tokens[self.current].tokenType == TokenType.LPAREN:
                lp = self.tokens[self.current]
                self.current += 1
                part = self.parseExpr()
                if (not self.valid()) or self.tokens[self.current].tokenType != TokenType.RPAREN:
                    raise Exception("No ) found for " + lp.toString(False))
                rp = self.tokens[self.current]
                self.current += 1
                return Grouping(lp, part, rp)
            else:
                if self.tokens[self.current].tokenType == TokenType.NUMBER:
                    literal = self.tokens[self.current]
                    self.current += 1
                    return Literal(literal)
                raise Exception("Expected Number got : " + self.tokens[self.current].toString(True))
        else:
            raise Exception("Invalid syntax")
            
    def parsePrimary(self):
        result = self.parseLiteral()
        while self.valid() and self.tokens[
            self.current
        ].tokenType in [TokenType.EXP]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parsePrimary()
            result = BinaryExpr(result, op, part2)
        return result

    def parseFactor(self):
        if self.valid():
            if self.tokens[self.current].tokenType == TokenType.MINUS:
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
        while self.valid() and self.tokens[
            self.current
        ].tokenType in [TokenType.MULT, TokenType.DIV]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseFactor()
            result = BinaryExpr(result, op, part2)
        return result

    def parseExpr(self):
        result = self.parseTerm()
        while self.valid() and self.tokens[
            self.current
        ].tokenType in [TokenType.PLUS, TokenType.MINUS]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseTerm()
            result = BinaryExpr(result, op, part2)
        return result
    
    def parse(self):
        expr = self.parseExpr()
        if self.current != len(self.tokens):
            raise Exception("invalid syntax")
        return expr        