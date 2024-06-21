from abc import ABC, abstractmethod
import os

from lexing.lexer_generator.finite_automata import DFA
from parsing.parser_generator_lr.parsing_table import ParsingTable


class Grammar(ABC):
    def __init__(
            self, 
            name,
            non_terminals : list[str],
            terminals : list[str],
            start_symbol : str,
            productions : dict[str, list[list[str]]]
    ):
        self.name = name
        self.EOF = "$"
        self.non_terminals = non_terminals
        self.terminals = terminals + [self.EOF]
        self.start_symbol = start_symbol
        self.productions = productions
        self.automaton = self.buildAutomaton()

    # this method should be abstract
    @abstractmethod
    def buildAutomaton(self) -> DFA:
        pass

    @abstractmethod
    def bpt(self) -> ParsingTable:
        pass

    def BuildParsingTable(self, reuse = True) -> ParsingTable:
        if self.table_exist() and reuse:
            return ParsingTable.load_parsing_table(self.name)
        else:
            pt = self.bpt()
            pt.save_parsing_table(self.name)
            return pt

    def is_production(self, prod : list[str]) -> bool:
        for key in self.productions:
            for pr in self.productions[key]:
                if pr == prod:
                    return True
        return False
    
    def find_key_given_prod(self, prod : list[str]) -> str:
        for key in self.productions:
            for pr in self.productions[key]:
                if pr == prod:
                    return key
        return ""

    def find_st_given_item(self, itemToFound) -> list[int]:
        result = []
        for st in range(0, self.automaton.total_states):
            for item in self.automaton.additional_info[st]:
                if itemToFound == item:
                    result.append(st)
        return result
    
    def table_exist(self) -> bool:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the file within common/grammartable
        # Adjust dir_path to go up to the src/ directory
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        filepath = os.path.join(dir_path, "common", "grammarTables", self.name)
        return os.path.exists(filepath)