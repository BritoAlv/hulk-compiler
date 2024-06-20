class Token:
    def __init__(self, type : str, lexeme = "", line = 0 , offsetLine  = 0):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.offsetLine = offsetLine

    def __str__(self, short = False):
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