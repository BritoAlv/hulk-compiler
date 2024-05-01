from enum import Enum

class TokenType(Enum):
    NUMBER = "NUMBER"

    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    LPAREN = "("
    RPAREN = ")"

    SPACE = " "
    ESCAPE1 = "\r"
    TAB = "\t"
    NEWLINE = "\n"

    ILLEGAL = "ILLEGAL"
    EOF = "EOF"


digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
constLex = [
    TokenType.PLUS,
    TokenType.MINUS,
    TokenType.MULT,
    TokenType.DIV,
    TokenType.LPAREN,
    TokenType.RPAREN,
    TokenType.SPACE,
    TokenType.ESCAPE1,
    TokenType.TAB,
    TokenType.NEWLINE,
]

constIgnore = [TokenType.SPACE, TokenType.ESCAPE1, TokenType.TAB, TokenType.NEWLINE]


class Token:
    def __init__(self, tokenType, lexeme, literal, line):
        self.tokenType = tokenType
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def toString(self, short):
        if short:
            return str(self.tokenType.value)
        return (
            str(self.tokenType.value)
            + " "
            + self.lexeme
            + " "
            + str(self.literal)
            + " at line "
            + str(self.line)
        )


def convert_number(inp):
    return int(inp, 10)


def automataNumber(offset, inputStr, line):
    if inputStr[offset] in digits:
        ed = offset
        while ed + 1 < len(inputStr[offset]) and inputStr[ed + 1] in digits:
            ed += 1
        lexeme = inputStr[offset : ed + 1]
        return Token(TokenType.NUMBER, lexeme, convert_number(lexeme), line)
    return None

def automataConst(offset, inputStr, line):
    for const in constLex:
        value = const.value
        lenn = len(value)
        if offset + lenn <= len(inputStr):
            lexeme = inputStr[offset : offset + lenn]
            if lexeme == value:
                return Token(const, lexeme, None, line)
    return None

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