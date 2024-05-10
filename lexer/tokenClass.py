class Token:
    def __init__(self, tokenType, lexeme, literal, line):
        self.tokenType = tokenType
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.position = 0

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