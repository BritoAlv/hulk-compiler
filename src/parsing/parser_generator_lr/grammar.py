from common import token_class
from lexer_generator import LexerGenerator, const
import finite_automata 


EPSILON = ""
EOF = "$"
ERROR = "ERROR"
DUMMY = "S'"

class Grammar:
    # Parameters
    def __init__(
        self,
        non_terminals: list[str],
        terminals: list[str],
        start_terminal: str,
        productions: dict[str, list[list[str]]],
    ) -> None:
        # Body
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.start_terminal = start_terminal
        self.productions = productions
        productions[DUMMY] = [[self.start_terminal, EOF]]

        