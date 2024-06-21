from common.token_class import Token
from lexing.lexer_generator  import lexer_generator

class Lexer:
    def __init__(self, specs: list[tuple[str, str]]):
        self.specs = specs
        lexGen = lexer_generator.LexerGenerator()
        self.automatas = [lexGen.Compile(x[1]) for x in specs]
        self.currentLine = 0
        self.positionInLine = 0

    def scanTokens(self, inputStr: str) -> list[Token]:
        self.currentLine = 0
        self.positionInLine = 0
        tokens = []
        cr = 0
        while cr < len(inputStr):
            if inputStr[cr] in [" ", "\n", "\t", "\r"]:
                if inputStr[cr] == "\n":
                    self.currentLine += 1
                    self.positionInLine = 0
                cr += 1
                continue
            elif inputStr[cr] == "#":
                while cr < len(inputStr) and inputStr[cr] != "\n":
                    cr += 1
                self.currentLine += 1
                self.positionInLine = 0
                cr += 1
                continue
            tok = self.scanToken(inputStr, cr)
            for i in range(cr, cr + len(tok.lexeme)):
                if inputStr[i] == "\n":
                    self.currentLine += 1
                    self.positionInLine = 0
                else:
                    self.positionInLine += 1
            cr += len(tok.lexeme)
            tokens.append(tok)
        tokens.append(Token("$", "$", self.currentLine, self.positionInLine))
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
                if matched == (-1, -1) or matched[1] < longest_matched:
                    matched = (i, longest_matched)

        if matched == (-1, -1):
            shift = 1
            while offset + shift + 1 < len(inputStr) and inputStr[offset + shift + 1] != " ":
                shift += 1
            return Token("Error", inputStr[offset: offset + shift], self.currentLine, self.positionInLine)
        return Token(
            self.specs[matched[0]][0],
            inputStr[offset : matched[1]],
            self.currentLine,
            self.positionInLine,
        )