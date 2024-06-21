import string

from common import constants as const

letter = ""

for let in string.ascii_letters:
    letter += let +  const.plus
letter = letter[:-2]
letter = const.opar + letter + const.cpar

digits = ""
for dig in string.digits:
    digits += dig + const.plus
digits = digits[:-2]
digits = const.opar + digits + const.cpar

digits_greater_zero = const.opar
for dig in string.digits:
    if int(dig) > 0:
        digits_greater_zero += dig + const.plus
digits_greater_zero = digits_greater_zero[:-2]
digits_greater_zero += const.cpar

identifier = letter + const.opar + letter + const.plus + digits + const.plus + "_"  +  const.cpar + const.star 

number1 = const.opar + digits_greater_zero + digits + const.star + const.cpar
number2 = const.opar + digits + digits + const.star + "." + digits + digits + const.star + const.cpar
number3 = const.opar + "0" + const.cpar

number = const.opar + number1 + const.plus + number2 + const.plus + number3 +  const.cpar

stringg = "\"" + const.opar + digits + const.plus + letter + const.cpar + "\""

from lexing.lexer.lexer import Lexer

hulk_lexer = Lexer(
    [
        ("powerOp", "^"),
        ("modOp", "%"),
        ("strOp", "@"),
        ("extends", "extends"),
        ("lbracket", "["),
        ("rbracket", "]"),
        ("lbrace", "{"),
        ("rbrace", "}"),
        ("lparen", "("),
        ("rparen", ")"),
        ("greater", ">"),
        ("less", "<"),
        ("semicolon", ";"),
        ("colon", ":"),
        ("comma", ","),
        ("type", "type"),
        ("arrow", "->"),
        ("equal", "="),
        *[(x, x) for x in ["if", "else", "elif", "protocol", "in", "let", "function", "inherits", "extends", "while", "for", "true", "false", "self", "new"]],
        ("destrucOp", ":="),
        ("doubleOr", "||"),
        ("or", "|"),
        ("and", "&"),
        ("doubleEqual", "=="),
        ("notEqual", "!="),
        ("greaterEq", ">="),
        ("lessEq", "<="),
        ("plus", "+"),
        ("minus", "-"),
        ("start", "*"),
        ("div", "/"),
        ("dot", "."),
        ("id", identifier),
        ("number", number),
        ("string", stringg)
    ]
)