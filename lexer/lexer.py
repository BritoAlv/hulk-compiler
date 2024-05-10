from lexer.automata import automataIdentifier, automataNumber, automateConstGenerator
from lexer.tokenClass import *
from lexer.tokenType import *


class Lexer:
    def __init__(self, inputStr):
        self.inputStr = inputStr
        self.tokens = []
        self.line = 1
        self.automatas = [
            automataNumber,
            automataIdentifier,
            *[automateConstGenerator(x) for x in constLex],
        ]

    def scanToken(self, offset):
        result = Token(TokenType.ILLEGAL, "", None, self.line)
        for automat in self.automatas:
            tk = automat(offset, self.inputStr, self.line)
            if tk is not None:
                if len(result.lexeme) < len(tk.lexeme):
                    result = tk
        if result.tokenType == TokenType.ILLEGAL:
            result.lexeme = self.inputStr[offset]
        result.position = offset
        return result

    def scan_tokens(self):
        cr = 0
        wrong = []
        while cr < len(self.inputStr):
            tok = self.scanToken(cr)
            cr += len(tok.lexeme)
            if tok.tokenType == TokenType.ILLEGAL:
                wrong.append(tok)
            if tok.tokenType not in constIgnore:
                self.tokens.append(tok)
            for t in tok.lexeme:
                if t == "\n":
                    self.line += 1
        if len(wrong) > 0:
            raise Exception("Lexer failed")
