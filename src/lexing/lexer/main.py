import string
from lexing.lexer_generator import const
from lexer import Lexer
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

digits_greater_zero = const.opar + "1+2+3+4+5+6+7+8+9" + const.cpar

identifier = letter + const.opar + letter + const.plus + digits + const.plus + "_" + const.plus +  const.cpar + const.star 

number = const.opar + digits_greater_zero + digits + const.star + const.opar + "." + digits + const.star + const.cpar + const.question + const.cpar

stringg = "\"" + const.opar + digits + const.plus + letter + const.cpar + "\""

print(identifier, number, stringg)

lexer = Lexer(
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
        *[(x, x) for x in ["if", "else", "elif", "protocol", "in", "let", "function", "inherits", "extends", "while", "for", "true", "false", "self"]],
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
        ("string", stringg),
    ]
)

print("Done building the lexer and its automatas")