import os
import pickle
from common.token_class import Token
from lexing.lexer_generator  import lexer_generator
from lexing.lexer_generator.finite_automata import DFA 
class Lexer:
    def __init__(self, specs: list[tuple[str, str]]):
        self.specs = specs
        lexGen = lexer_generator.LexerGenerator()
        self.automatas = []
        for x in specs:
            if self.exist_dfa(x[0]):
                self.automatas.append(self.load_automata(x[0]))
            else:
                automata = lexGen.Compile(x[1])
                self.save_automata(x[0], automata)
                self.automatas.append(automata)
        self.currentLine = 0
        self.positionInLine = 0
        self.errors : list[Token] = []

    def report(self, inputStr: str) -> bool:
        if len(self.errors) > 0:
            for error in self.errors:
                line =  error.line
                position = error.offsetLine
                lines = inputStr.split("\n")
                error_line = lines[line]
                print(f"Error on line {line}, " + error.type +  ":")
                print(error_line)
                print(" " * (position-1) + "^")
            return True
        return False

    def sanity_check(self, tokens: list[Token]):
        marked = [False for _ in range(0, len(tokens))]
        self.after_num(tokens, marked)
        self.unterminated_string_literal(tokens, marked)
        for i in range(len(marked)-1, -1, -1):
            if marked[i]:
                tokens.pop(i)

        for x in tokens:
            if x.type == "Error":
                self.errors.append(Token("Invalid Symbol", x.lexeme, x.line, x.offsetLine))
        
    def after_num(self, tokens: list[Token], marked : list[bool]):
        for i in range(0, len(tokens) - 1):
            if tokens[i].type == "number" and tokens[i + 1].type == "number" and not marked[i]:
                self.errors.append(Token("Invalid Number Format", tokens[i].lexeme, tokens[i].line, tokens[i].offsetLine))
                marked[i] = marked[i+1] = True
            if tokens[i].type == "number" and tokens[i+1].type == "id" and not marked[i]:
                self.errors.append(Token("Identifier can't start with number", tokens[i].lexeme, tokens[i].line, tokens[i].offsetLine))
                marked[i] = marked[i+1] = True

    def unterminated_string_literal(self, tokens : list[Token], marked : list[bool]):
        for i in range(0, len(tokens)):
            if tokens[i].type == "Error" and tokens[i].lexeme[0] == "\"" and not marked[i]:
                self.errors.append(Token("Unterminated String Literal", tokens[i].lexeme, tokens[i].line, tokens[i].offsetLine))
                marked[i] = True
    
            

    def scanTokens(self, inputStr: str) -> list[Token]:
        self.currentLine = 0
        self.positionInLine = 0
        self.errors = []
        tokens = []
        cr = 0
        while cr < len(inputStr):
            if inputStr[cr] in [" ", "\n", "\t", "\r"]:
                if inputStr[cr] == "\n":
                    self.currentLine += 1
                    self.positionInLine = 0
                cr += 1
                self.positionInLine += 1
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
            tok.lexeme = tok.lexeme.replace("\\\"", "\"")
            tokens.append(tok)
        tokens.append(Token("$", "$", self.currentLine, self.positionInLine))
        self.sanity_check(tokens)
        return tokens

    def scanToken(self, inputStr: str, offset: int):
        matched = (-1, -1)
        for i in range(0, len(self.automatas)):
            longest_matched = -1
            cr = offset
            st = self.automatas[i].start_state
            while cr < len(inputStr) and self.automatas[i].next_state(inputStr[cr], st) != -1:
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
            tok = Token("Error", inputStr[offset: offset + shift + 1], self.currentLine, self.positionInLine)
            return tok
        return Token(
            self.specs[matched[0]][0],
            inputStr[offset : matched[1]],
            self.currentLine,
            self.positionInLine,
        )
    
    def save_automata(self, name: str, automata : DFA):
        # Get the directory of the current file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the file within common/grammartable
        # Adjust dir_path to go up to the src/ directory
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        filepath = os.path.join(dir_path, "common", "automatas", name)
        with open(filepath, "wb") as file:
            pickle.dump(automata, file)

    def load_automata(self, name: str):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the file within common/grammartable
        # Adjust dir_path to go up to the src/ directory
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        filepath = os.path.join(dir_path, "common", "automatas", name)
        with open(filepath, "rb") as file:
            return pickle.load(file)

    def exist_dfa(self, name : str):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the file within common/grammartable
        # Adjust dir_path to go up to the src/ directory
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        filepath = os.path.join(dir_path, "common", "automatas", name)
        return os.path.exists(filepath)