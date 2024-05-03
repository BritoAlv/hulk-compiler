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