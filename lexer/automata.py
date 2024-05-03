from lexer.tokenClass import Token
from lexer.tokenType import *

def convert_number(inp):
    return 

def automataNumber(offset, inputStr, line):
    if inputStr[offset].isdigit():
        ed = offset
        while ed + 1 < len(inputStr[offset]) and  inputStr[ed + 1].isdigit() :
            ed += 1
        lexeme = inputStr[offset : ed + 1]
        return Token(TokenType.NUMBER, lexeme, int(lexeme, 10), line)
    return None

def automateConstGenerator(const):
    def automataConst(offset, inputStr, line):
        value = const.value
        lenn = len(value)
        if offset + lenn <= len(inputStr):
            lexeme = inputStr[offset : offset + lenn]
            if lexeme == value:
                return Token(const, lexeme, None, line)
        return None
    return automataConst