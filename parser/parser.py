from lexer.lexer import *
from visitors.visitor import *
from parser.expressions import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def valid(self):
        return self.current < len(self.tokens)

    def current_tokenType(self):
        return self.tokens[self.current].tokenType

    def advance_check(self, *tokenType):
        for tok in tokenType:
            if self.valid() and self.current_tokenType() == tok:
                t = self.tokens[self.current]
                self.current += 1
                return t
        message = "Expected some token of kind: ["
        for tok in tokenType:
            message += tok.value
            message += ", "
        message += "]"
        raise Exception(message)

    def check(self, *tokenType):
        for tok in tokenType:
            if self.valid() and self.current_tokenType() == tok:
                return True
        return False

    def parseLiteral(self):
        if self.check(TokenType.LPAREN):
            lp = self.advance_check(TokenType.LPAREN)
            part = self.parseTernary()
            rp = self.advance_check(TokenType.RPAREN)
            return Grouping(lp, part, rp)
        else:
            return Literal(self.advance_check(TokenType.NUMBER))

    def parsePrimary(self):
        result = self.parseLiteral()
        if self.check(TokenType.EXP):
            op = self.advance_check(TokenType.EXP)
            part2 = self.parsePrimary()
            result = BinaryExpr(result, op, part2)
        return result

    def parseFactor(self):
        operators = [TokenType.MINUS, TokenType.NOT]
        if self.check(*operators):
            op = self.advance_check(*operators)
            part = self.parseTernary()
            return UnaryExpr(op, part)
        else:
            return self.parsePrimary()

    def parseTerm(self):
        operators = [
            TokenType.MULT,
            TokenType.DIV,
            TokenType.AND,
            TokenType.NAND,
        ]
        result = self.parseFactor()
        while self.check(*operators):
            op = self.advance_check(*operators)
            part2 = self.parseFactor()
            result = BinaryExpr(result, op, part2)
        return result

    def parseExpr(self):
        operators = [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.SHIFT_LEFT,
            TokenType.SHIFT_RIGHT,
            TokenType.OR,
            TokenType.XOR,
        ]
        result = self.parseTerm()
        while self.check(*operators):
            op = self.advance_check(*operators)
            part2 = self.parseTerm()
            result = BinaryExpr(result, op, part2)
        return result

    def parseEq(self):
        operators = [
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
        ]
        result = self.parseExpr()
        if self.check(*operators):
            op = self.advance_check(*operators)            
            part2 = self.parseEq()
            result = BinaryExpr(result, op, part2)
        return result

    def parseTernary(self):
        result = self.parseEq()
        if self.check(TokenType.TERNARY_COND):
            op1 = self.advance_check(TokenType.TERNARY_COND)
            middle = self.parseTernary()
            op2 = self.advance_check(TokenType.TERNARY_SEP)
            right = self.parseTernary()
            return TernaryExpr(result, op1, middle, op2, right)
        return result

    def parseStatment(self):
        if self.check(TokenType.PRINT_STATMENT):
            op1 = self.advance_check(TokenType.PRINT_STATMENT)
            self.advance_check(TokenType.LPAREN)
            expr = self.parseTernary()
            self.advance_check(TokenType.RPAREN)
            self.advance_check(TokenType.END_STATMENT)
            return UnaryExpr(op1, expr)
        else:
            expr = self.parseTernary()
            self.advance_check(TokenType.END_STATMENT)
            return expr

    def parseProgram(self):
        statments = []
        while self.valid():
            statments.append(self.parseStatment())
        return statments