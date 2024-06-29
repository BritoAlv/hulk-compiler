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
    def __eq__(self, value: object) -> bool:
        if type(value) != Token:
            return False
        return self.type == value.type and self.lexeme == value.lexeme and self.line == value.line and self.offsetLine == value.offsetLine