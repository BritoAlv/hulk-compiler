from lexer.lexer import *
from parser.visitor import *
from parser.expressions import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parsePrimary(self):
        if self.current < len(self.tokens):
            if self.tokens[self.current].tokenType == TokenType.LPAREN:
                lp = self.tokens[self.current]
                self.current += 1
                part = self.parseExpr()
                rp = self.tokens[self.current]
                self.current += 1
                return Grouping(lp, part, rp)
            else:
                literal = self.tokens[self.current]
                self.current += 1
                return Literal(literal)
        else:
            return None        

    def parseFactor(self):
        if self.current < len(self.tokens):
            if self.tokens[self.current].tokenType == TokenType.MINUS:
                op = self.tokens[self.current]
                self.current += 1
                part = self.parseExpr()
                return UnaryExpr(op, part)
            else:
                return self.parsePrimary()
        else:
            return None

    def parseTerm(self):
        result = self.parseFactor()
        while self.current < len(self.tokens) and self.tokens[self.current].tokenType in [TokenType.MULT, TokenType.DIV]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseFactor()
            result = BinaryExpr(result, op, part2)
        return result

    def parseExpr(self):
        result = self.parseTerm()
        while self.current < len(self.tokens) and self.tokens[self.current].tokenType in [TokenType.PLUS, TokenType.MINUS]:
            op = self.tokens[self.current]
            self.current += 1
            part2 = self.parseTerm()
            result = BinaryExpr(result, op, part2)
        return result