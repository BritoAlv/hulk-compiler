from lexer_generator.lexer_generator import LexerGenerator
from tokenClass import Token

class Lexer:
    def __init__(self, specs: list[tuple[str, str]]):
        self.specs = specs
        self.automatas = [LexerGenerator.Parse(x[1]) for x in specs]
        self.currentLine = 0
        self.positionInLine = 0

    def scanTokens(self, inputStr: str):
        tokens = []
        cr = 0
        while cr < len(inputStr):
            if inputStr[cr] in [" ", "/n", "/t", "/r"]:
                if inputStr[cr] == "/n":
                    self.currentLine += 1
                    self.positionInLine = 0
                cr += 1
                continue
            tok = self.scanToken(inputStr, cr)
            for i in range(cr, cr + len(tok.lexeme)):
                if inputStr[i] == "/n":
                    self.currentLine += 1
                    self.positionInLine = 0
            cr += len(tok.lexeme)
            self.positionInLine += len(tok.lexeme)
            tokens.append(tok)
        tokens.append(Token("EOF", "", self.currentLine, self.positionInLine))
        return tokens

    def scanToken(self, inputStr: str, offset: int):
        matched = (-1, -1)
        for i in range(0, len(self.automatas)):
            longest_matched = -1
            cr = offset
            st = self.automatas[i].start_state
            while (
                cr < len(inputStr)
                and self.automatas[i].next_state(inputStr[cr], st) != -1
            ):
                st = self.automatas[i].next_state(inputStr[cr], st)
                cr += 1
                if st in self.automatas[i].accepting_states:
                    longest_matched = cr
            if longest_matched != -1:
                if matched == (-1, -1) or matched[1] < (longest_matched):
                    matched = (i, longest_matched)

        if matched == (-1, -1):
            return Token("Error", "", self.currentLine, self.positionInLine)
        return Token(
            self.specs[i][0],
            inputStr[offset : self.specs[i][1]],
            self.currentLine,
            self.positionInLine,
        )

lexer = Lexer(
    [
        ("PLUS", "+"),
        ("GREATER_EQUAL", ">="),
        (
            "NUMBER",
            "(1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 0)(0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9)*",
        ),
    ]
)