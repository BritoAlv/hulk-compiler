from lexer.tokenClass import *
from lexer.tokenType import *


class Lexer:
    def __init__(self, inputStr, automatas):
        self.inputStr = inputStr
        self.tokens = []
        self.line = 1
        self.automatas = automatas

    def scanToken(self, offset):
        for automat in self.automatas:
            tk = automat(offset, self.inputStr, self.line)
            if tk is not None:
                return tk
        return Token(TokenType.ILLEGAL, " ", None, self.line)

    def scanTokens(self):
        cr = 0
        while cr < len(self.inputStr):
            tok = self.scanToken(cr)
            cr += len(tok.lexeme)
            if tok.tokenType not in constIgnore:
                self.tokens.append(tok)
            for t in tok.lexeme:
                if t == "\n":
                    line += 1