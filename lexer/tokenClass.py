class Token:
    def __init__(self, tokenType : str, lexeme : str, line : int, offsetLine : int):
        self.tokenType = tokenType
        self.lexeme = lexeme
        self.line = line
        self.offsetLine = offsetLine

    def toString(self, short):
        if short:
            return self.tokenType
        return (
            self.tokenType
            + " "
            + self.lexeme
            + " "
            " at line "
            + str(self.line)
            + " "
            + "at position "
            + str(self.offsetLine)
            + " "
        )