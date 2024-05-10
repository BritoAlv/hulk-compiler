from lexer.tokenClass import Token
from lexer.tokenType import *

def automataLineComment(offset, inputStr, line):
    if offset + 1 < len(inputStr) and inputStr[offset] == "/" and inputStr[offset + 1] == "/":
        ed = offset + 2
        while ed < len(inputStr) and inputStr[ed] != "\n":
            ed += 1
        return Token(TokenType.LINE_COMMENT, inputStr[offset : ed], None, line)
    return None

def automataNumber(offset, inputStr, line):
    if inputStr[offset].isdigit():
        ed = offset
        while ed + 1 < len(inputStr) and inputStr[ed + 1].isdigit() :
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

def automataIdentifier(offset, inputStr, line):
    if str.isalpha(inputStr[offset]):
        ed = offset
        while ed + 1 < len(inputStr) and (str.isalpha(inputStr[ed + 1]) or str.isnumeric(inputStr[ed + 1]) or inputStr[ed + 1] == "_"):
            ed += 1
        ident = inputStr[offset : ed + 1]
        for resWord in constRes:
            if resWord.value == ident:
                return Token(resWord, ident, None, line)
        return Token(TokenType.IDENTIFIER, ident, None, line)