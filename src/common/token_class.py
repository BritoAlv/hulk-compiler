class Token:
    def __init__(self, type : str, lexeme : str, line : int, offsetLine : int):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.offsetLine = offsetLine

    def toString(self, short):
        if short:
            return self.type
        return (
            self.type
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