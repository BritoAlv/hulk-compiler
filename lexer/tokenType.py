from enum import Enum

class TokenType(Enum):
    NUMBER = "NUMBER"

    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    EXP = "**"
    DIV = "/"
    LPAREN = "("
    RPAREN = ")"
    
    GREATER_EQUAL = ">="
    GREATER = ">"
    LESS = "<"
    LESS_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="

    SHIFT_LEFT = "<<"
    SHIFT_RIGHT = ">>"

    AND = "and"
    NOT = "not"
    OR = "or"
    XOR = "xor"
    NAND = "nand"

    TERNARY_COND = "?"
    TERNARY_SEP = ":"

    IDENTIFIER = "ID"

    END_STATMENT = ";"
    PRINT_STATMENT = "print"

    SPACE = " "
    ESCAPE1 = "\r"
    TAB = "\t"
    NEWLINE = "\n"

    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

constRes = [
    TokenType.AND,
    TokenType.NOT,
    TokenType.OR,
    TokenType.XOR,
    TokenType.NAND,
    TokenType.PRINT_STATMENT
]

constLex = [
    TokenType.TERNARY_COND,
    TokenType.TERNARY_SEP,
    TokenType.GREATER_EQUAL,
    TokenType.GREATER,
    TokenType.LESS,
    TokenType.LESS_EQUAL,
    TokenType.EQUAL,
    TokenType.NOT_EQUAL,
    TokenType.END_STATMENT,

    TokenType.SHIFT_LEFT,
    TokenType.SHIFT_RIGHT,

    TokenType.EXP,
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