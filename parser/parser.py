from lexer.lexer import *
from parser.statments import *
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
        elif self.check(TokenType.NUMBER):
            return Literal(self.advance_check(TokenType.NUMBER))
        else:
            iden = Variable(self.advance_check(TokenType.IDENTIFIER))
            if self.check(TokenType.LPAREN):
                op = self.advance_check(TokenType.LPAREN)
                args = []
                if not self.check(TokenType.RPAREN):
                    args = self.parseArguments()
                self.advance_check(TokenType.RPAREN)
                callbase = CallExpr(iden, op, args)
                while self.check(TokenType.LPAREN):
                    op = self.advance_check(TokenType.LPAREN)
                    args = []
                    if not self.check(TokenType.RPAREN):
                        args = self.parseArguments()
                    self.advance_check(TokenType.RPAREN)
                    callbase = CallExpr(callbase, op, args)    
                return callbase
            return iden

    def parseArguments(self):
        args = []
        args.append(self.parseTernary())
        while self.check(TokenType.ARG_SEPARATOR):
            self.advance_check(TokenType.ARG_SEPARATOR)
            args.append(self.parseTernary())
        return args

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

    def parseAssignment(self):
        expr = self.parseTernary()
        if self.check(TokenType.ASSIGN):
            op1 = self.advance_check(TokenType.ASSIGN)
            expr2 = self.parseAssignment()
            if not isinstance(expr, Variable):
                raise Exception("Left side is not a variable")
            return AssignStatement(expr, expr2)
        return expr

    def parseBlock(self):
        op1 = self.advance_check(TokenType.LBRACE)
        statments = []
        while True:
            statments.append(self.parseDeclaration())
            if self.check(TokenType.RBRACE):
                break
        self.advance_check(TokenType.RBRACE)
        return BlockStatement(statments)

    def parseIf(self):
        op1 = self.advance_check(TokenType.IF)
        self.advance_check(TokenType.LPAREN)
        condition = self.parseTernary()
        self.advance_check(TokenType.RPAREN)
        then = self.parseStatment()
        otherwise = None
        if self.check(TokenType.ELSE):
            self.advance_check(TokenType.ELSE)
            otherwise = self.parseStatment()
        return IfStatement(condition, then, otherwise)

    def parseFor(self):
        op1 = self.advance_check(TokenType.FOR)
        op2 = self.advance_check(TokenType.LPAREN)
        initializer = None
        condition = None
        action = None
        if self.check(TokenType.VAR):
            initializer = self.parseVar()
        else:
            self.advance_check(TokenType.END_STATMENT)

        if not self.check(TokenType.END_STATMENT):
            condition = self.parseTernary()
        self.advance_check(TokenType.END_STATMENT)

        if not self.check(TokenType.RPAREN):
            action = self.parseAssignment()
        op3 = self.advance_check(TokenType.RPAREN)
        block = self.parseStatment()
        return ForStatement(initializer, condition, action, block)

    def parseWhile(self):
        op1 = self.advance_check(TokenType.WHILE)
        self.advance_check(TokenType.LPAREN)
        condition = self.parseTernary()
        self.advance_check(TokenType.RPAREN)
        then = self.parseStatment()
        return WhileStatement(condition, then)

    def parsePrint(self):
        op1 = self.advance_check(TokenType.PRINT_STATMENT)
        self.advance_check(TokenType.LPAREN)
        expr = self.parseAssignment()
        self.advance_check(TokenType.RPAREN)
        self.advance_check(TokenType.END_STATMENT)
        return PrintStatement(op1, expr)

    def parseBreak(self):
        self.advance_check(TokenType.BREAK)
        self.advance_check(TokenType.END_STATMENT)
        return BreakStatement()

    def parseContinue(self):
        self.advance_check(TokenType.CONTINUE)
        self.advance_check(TokenType.END_STATMENT)
        return ContinueStatement()

    def parseReturn(self):
        expr = None
        self.advance_check(TokenType.RETURN)
        if not self.check(TokenType.END_STATMENT):
            expr = self.parseTernary()
        self.advance_check(TokenType.END_STATMENT)
        return ReturnStatement(expr)
    
    def parseFunctionDeclaration(self):
        self.advance_check(TokenType.DEF)
        op = self.advance_check(TokenType.IDENTIFIER)
        name = op.lexeme
        self.advance_check(TokenType.LPAREN)
        params = []
        while not self.check(TokenType.RPAREN):
            params.append(self.advance_check(TokenType.IDENTIFIER))
            if not self.check(TokenType.ARG_SEPARATOR):
                break
            self.advance_check(TokenType.ARG_SEPARATOR)
        self.advance_check(TokenType.RPAREN)
        body = self.parseBlock()
        return FunctionDeclaration(name, params, body)
    
    def parseStatment(self):
        if self.check(TokenType.PRINT_STATMENT):
            return self.parsePrint()
        elif self.check(TokenType.LBRACE):
            return self.parseBlock()
        elif self.check(TokenType.CONTINUE):
            return self.parseContinue()
        elif self.check(TokenType.BREAK):
            return self.parseBreak()
        elif self.check(TokenType.IF):
            return self.parseIf()
        elif self.check(TokenType.RETURN):
            return self.parseReturn()
        elif self.check(TokenType.FOR):
            return self.parseFor()
        elif self.check(TokenType.WHILE):
            return self.parseWhile()
        elif self.check(TokenType.DEF):
            return self.parseFunctionDeclaration()
        elif self.check(TokenType.LBRACE):
            return self.parseBlock()
        else:
            expr = self.parseAssignment()
            self.advance_check(TokenType.END_STATMENT)
            return expr
    
    def parseVar(self):
        op1 = self.advance_check(TokenType.VAR)
        identifier = self.advance_check(TokenType.IDENTIFIER)
        if self.check(TokenType.ASSIGN):
            self.advance_check(TokenType.ASSIGN)
            expr = self.parseAssignment()
        self.advance_check(TokenType.END_STATMENT)
        return VariableDeclarationStatement(op1, identifier, expr)
    
    def parseDeclaration(self):
        expr = None
        if self.check(TokenType.VAR):
            return self.parseVar()
        return self.parseStatment()
    
    def parseProgram(self):
        statments = []
        while self.valid():
            statments.append(self.parseDeclaration())
        return statments