import os
from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *
from common.constants import EOF

import pickle

MAX_LEN_REPAIR = 4
CONSECUTIVE_INSERTS_MAX = 3
MAX_NUMBER_SHIFTS = 4

class ParsingTable:
    def __init__(
        self,
        total_states: int,
        terminals: list[str],
        non_terminals: list[str],
        productions: dict[str, list[list[str]]],
        attributed_productions=None,
    ):
        self.table_input: list[dict] = [{} for i in range(0, total_states)]
        self.table_nonterminals = [{} for i in range(0, total_states)]
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions
        self.attributed_productions = attributed_productions

    def save_parsing_table(self, filename):
        # Get the directory of the current file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the file within common/grammartable
        # Adjust dir_path to go up to the src/ directory
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        filepath = os.path.join(dir_path, "common", "grammarTables", filename)
        with open(filepath, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_parsing_table(filename):
        # Get the directory of the current file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the file within common/grammartable
        # Adjust dir_path to go up to the src/ directory
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        filepath = os.path.join(dir_path, "common", "grammarTables", filename)
        with open(filepath, "rb") as file:
            return pickle.load(file)

    def add_reduce_transition(self, st: int, terminal: str, key: str, len: int):
        if terminal in self.table_input[st]:
            if self.table_input[st][terminal][0] == "s":
                print(
                    "Grammar is not LR contains a shift reduce conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal][0] == "r":
                print(
                    "Grammar is not LR contains a reduce reduce conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal][0] == "a":
                print(
                    "Grammar is not LR, this state",
                    st,
                    " with therminal",
                    terminal,
                    "is supposed to be AC, not reduce",
                )
            return
        else:
            self.table_input[st][terminal] = ("r", key, len)

    def add_shift_transition(self, st: int, terminal: str, new_state: int):
        if terminal in self.table_input[st]:
            if (
                self.table_input[st][terminal][0] == "s"
                and self.table_input[st][terminal][1] != new_state
            ):
                print(
                    "Grammar is not LR contains a shift shift conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
                print("This is not supposed to happen")
            if self.table_input[st][terminal][0] == "r":
                print(
                    "Grammar is not LR contains a shift reduce conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal][0] == "a":
                print(
                    "Grammar is not LR, this state",
                    st,
                    " with therminal",
                    terminal,
                    "is supposed to be AC, not shift",
                )
            print("BOOM")
            return
        else:
            self.table_input[st][terminal] = ("s", new_state)

    def add_accept_transition(self, st: int, terminal: str):
        if terminal in self.table_input[st]:
            if self.table_input[st][terminal][0] == "s":
                print(
                    "Grammar is not LR contains a shift accept conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
                print("This is not supposed to happen")
            if self.table_input[st][terminal][0] == "r":
                print(
                    "Grammar is not LR contains a reduce accept conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            return
        else:
            self.table_input[st][terminal] = ("a", "accept")

    def add_nonterminal_transition(self, st: int, nonterminal: str, next_state: int):
        if (
            nonterminal in self.table_nonterminals[st]
            and self.table_nonterminals[st][nonterminal] != next_state
        ):
            print(
                "Two different transitions at state",
                st,
                "for non-terminal",
                nonterminal,
            )
        else:
            self.table_nonterminals[st][nonterminal] = next_state


    def parse(self, inputTokens: list[Token], inputStr = "") -> ParseTree:
        stackStates = []
        stackStates.append(0)
        stackParse: list[ParseNode] = []
        cr = 0
        while True:
            if inputTokens[cr].type not in self.table_input[stackStates[-1]]:
                print("There was a parsing error :")
                line =  inputTokens[cr].line
                position = inputTokens[cr].offsetLine
                lines = inputStr.split("\n")
                error_line = lines[line]
                print(f"Near error on line {line}, " + inputTokens[cr].type +  ":")
                for i in range(max(0, line -2), min(len(lines)-1, line + 2)):
                    print(i, lines[i])
                print("")
                print(line, error_line)
                print(line, " " * (position) + "^")
                print("Trying to recovery from error")
                self.recovery(stackStates, inputTokens[cr:])
                return ParseTree(ParseNode("ERROR"))

            next_action = self.table_input[stackStates[-1]][inputTokens[cr].type]
            if next_action[0] == "a":
                if cr != len(inputTokens) - 1:
                    print("Parsing done, with input is not at the $")
                    return ParseTree(ParseNode("ERROR"))
                else:
                    return ParseTree(stackParse[-1])
            if next_action[0] == "s":
                stackStates.append(next_action[1])
                new_node = ParseNode(inputTokens[cr].type)
                new_node.token = inputTokens[cr]
                stackParse.append(new_node)
                cr += 1
            if next_action[0] == "r":
                lenn = next_action[2]
                key = next_action[1]
                nodeResult = ParseNode(key)
                nodeResult.token = Token(key, key, 0, 0)
                for _ in range(0, lenn):
                    next = stackParse.pop()
                    nodeResult.children.append(next)
                    stackStates.pop()
                nodeResult.children.reverse()
                stackParse.append(nodeResult)
                assert stackParse[-1].value in self.table_nonterminals[stackStates[-1]]
                stackStates.append(
                    self.table_nonterminals[stackStates[-1]][stackParse[-1].value]
                )

    def get_index(self, tree: ParseNode):
        value = tree.value
        for i in range(0, len(self.productions[value])):  # type: ignore
            if len(self.productions[value][i]) == len(tree.children):  # type: ignore
                flag = True
                for j in range(0, len(tree.children)):
                    if tree.children[j].value != self.productions[value][i][j]:
                        flag = False
                if flag:
                    return i


    def fine(self, state) -> bool:
        top_stack = state.pstack[-1]
        top_tok = state.tokens[0]
        return (top_tok.type in self.table_input[top_stack] and (self.table_input[top_stack][top_tok.type][0] == 'a')) or state.ends_in_N_shifts()

    def bad(self, state) -> bool:
        op = CONSECUTIVE_INSERTS_MAX
        if len(state.repair) < op:
            return False
        
        pt = len(state.repair)-1
        while op > 0:
            if state.repair[pt][0] != "i":
                return False
            pt -= 1
            op -= 1
        return True


    def recovery(self, pstack : list[int], toks : list[Token]):
        """
        possible operations are:
            - insert Token.
            - delete.
            - shift.
        """
        visited = set()
        start = RecoveryItem(pstack, toks, [])
        visited.add(start)
        todo = [[start]]
        cur_cost = 0
        found = 0
        while cur_cost < len(todo):
            if len(todo[cur_cost]) == 0:
                if found:
                    break
                cur_cost += 1
                continue
            state = todo[cur_cost].pop()
            if self.fine(state):
                found = 1
                cur_cost = state.get_cost()

            if self.bad(state):
                continue

            for nbr in state.neighbours(self):
                cst = nbr.get_cost()
                if found and cst > cur_cost:
                    continue
                for _ in range(len(todo), cst + 1):
                    todo.append([])
                if nbr not in visited and nbr.rep_len() <= MAX_LEN_REPAIR:
                    todo[cst].append(nbr)
                    visited.add(nbr)
                    
                    
        if found:
            okey : set[RecoveryItem] = set()
            seen = set()
            queue = [x for x in visited]
            while len(queue) > 0:
                next = queue.pop()
                if next in seen:
                    continue
                seen.add(next)

                for nbr in next.neighbours(self):
                    if nbr.get_cost() <= cur_cost and nbr not in visited:
                        queue.append(nbr)

                if next.get_cost() == cur_cost and self.fine(next):
                    next.remove_trailing_shifts()
                    okey.add(next)

            for st in okey:
                st.show_error_recovery()

    def convertAst(self, tree: ParseNode):
        assert(isinstance(tree, ParseNode))
        assert(self.attributed_productions != None)
        body = tree.children
        s = []

        for i in range(0, len(body) + 1):
            s.append(None)

        b = []
        for i, node in enumerate(body, 1):
            if node != None:
                b.append(node.value)
                if node.value in self.terminals:
                    s[i] = node
                else:
                    s[i] = self.convertAst(body[i - 1])
        lambda_list = self.attributed_productions[tree.value]
        lambda_index = self.get_index(tree)
        return lambda_list[lambda_index](s)  # type: ignore

    def __str__(self):
        space = (
            max(
                20,
                max(
                    [len(x) for x in self.non_terminals]
                    + [len(x) for x in self.terminals]
                ),
            )
            * 2
        )
        header = (
            "State".ljust(space)
            + "".join([x.ljust(space) for x in self.terminals])
            + "".join([x.ljust(space) for x in self.non_terminals])
        )
        rows = [
            str(i).ljust(space)
            + "".join(
                [
                    (
                        str(self.table_input[i][x]).ljust(space)
                        if x in self.table_input[i]
                        else "".ljust(space)
                    )
                    for x in self.terminals
                ]
            )
            + "".join(
                [
                    (
                        str(self.table_nonterminals[i][x]).ljust(space)
                        if x in self.table_nonterminals[i]
                        else "".ljust(space)
                    )
                    for x in self.non_terminals
                ]
            )
            for i in range(0, len(self.table_input))
        ]
        return header + "\n" + "\n".join(rows)
    

class RecoveryItem:
    def __init__(self, pstack : list[int], tokens : list[Token], repair : list[tuple[str, Token]]):
        self.pstack = pstack.copy()
        self.tokens = tokens.copy()
        self.repair = repair.copy()

    def neighbours(self, ptable : ParsingTable):
        """
        get all neighbours of given state.
        """
        result = set()
        if len(self.tokens) > 0 and self.tokens[0].type != EOF and not (len(self.repair) > 0 and self.repair[-1][0] == "i"):
            result.add(RecoveryItem(self.pstack, self.tokens[1:], self.repair + [("d", self.tokens[0])]))
        
        for terminal in ptable.terminals:
            if terminal != EOF and terminal in ptable.table_input[self.pstack[-1]]:
                pstackCOPY = self.pstack.copy()
                next_action = ptable.table_input[pstackCOPY[-1]][terminal]
                if next_action[0] == "s":
                    pstackCOPY.append(next_action[1])
                    new_st = RecoveryItem(pstackCOPY, self.tokens, self.repair + [("i", Token(terminal, terminal, 0, 0))])
                if next_action[0] == "r":
                    lenn = next_action[2]
                    key = next_action[1]
                    for _ in range(0, lenn):
                        pstackCOPY.pop()
                    pstackCOPY.append(
                        ptable.table_nonterminals[pstackCOPY[-1]][key]
                    )
                    new_st = RecoveryItem(pstackCOPY, [Token(terminal, terminal, 0, 0)] +self.tokens, self.repair + [("i", Token(terminal, terminal, 0, 0))])
                result.add(new_st)

        if self.tokens[0].type in ptable.table_input[self.pstack[-1]]:
            pstackCOPY = self.pstack.copy()
            next_action = ptable.table_input[pstackCOPY[-1]][self.tokens[0].type]
            if next_action[0] == "s":
                pstackCOPY.append(next_action[1])
                result.add(RecoveryItem(pstackCOPY, self.tokens[1:], self.repair + [("s", self.tokens[0])]))
            if next_action[0] == "r":
                lenn = next_action[2]
                key = next_action[1]
                for _ in range(0, lenn):
                    pstackCOPY.pop()
                pstackCOPY.append(
                    ptable.table_nonterminals[pstackCOPY[-1]][key]
                )
                new_st = RecoveryItem(pstackCOPY, self.tokens, self.repair + [])
                if new_st != self:
                    result.add(new_st)
        
        return result

    def __str__(self) -> str:
        st = self.pstack.__str__() + " [" 
        for x in self.tokens:
            st += "(" + x.type + " " + x.lexeme +  ")"
        st += "]"
        
        st += "["
        for it in self.repair:
            st += "(op: " + it[0] + ", tok = " + it[1].type + " " + it[1].lexeme +  ")"
            st += ","
        st += "]"
        return st 

    def __hash__(self) -> int:
        mod = 10000007
        rs = 0
        for st in self.pstack:
            rs += st ** st
            rs %= mod

        for tk in self.tokens:
            nn = tk.lexeme.__hash__()**2 + tk.type.__hash__() + tk.line + tk.offsetLine
            rs += nn
            rs %= mod
        
        for seq in self.repair:
            tk = seq[1]
            nn = tk.lexeme.__hash__()**2 + tk.type.__hash__() + tk.line + tk.offsetLine
            rs += nn * seq[0].__hash__()
            rs %= mod
        
        return rs

    def __eq__(self, value: object) -> bool:
        if type(value) != RecoveryItem:
            return False

        if len(value.pstack) != len(self.pstack):
            return False

        for i in range(0, len(self.pstack)):
            if self.pstack[i] != value.pstack[i]:
                return False
            
        if len(value.tokens) != len(self.tokens):
            return False

        for i in range(0, len(self.tokens)):
            if self.tokens[i] != value.tokens[i]:
                return False
        
        
        if len(value.repair) != len(self.repair):
            return False

        for i in range(0, len(self.repair)):
            if self.repair[i] != value.repair[i]:
                return False
        return True

    def rep_len(self) -> int:
        pt = len(self.repair)-1
        while pt >= 0 and self.repair[pt][0] == "s":
            pt -= 1
        return pt + 1

    def ends_in_N_shifts(self) -> bool:
        op = MAX_NUMBER_SHIFTS
        if len(self.repair) < op:
            return False
        st = len(self.repair)-1
        while(op > 0):
            if self.repair[st][0] != "s":
                return False
            op -= 1
            st -= 1
        return True

    def remove_trailing_shifts(self):
        while len(self.repair) > 0 and self.repair[-1][0] == "s":
            self.repair.pop()

    def show_error_recovery(self):
        print("----------------")
        print("Seq: ")
        for x in self.repair:
            if(x[0] == "d"):
                print("delete", x[1])
            elif(x[0]  == "i"):
                print("insert", x[1].type)
            else:
                print("shift", x[1])
        print("----------------")

    def get_cost(self):
        """
        compute cost of a repair sequence.
        """
        ans = 0
        for x in self.repair:
            if x[0] == 'i' or x[0] == 'd':
                ans += 1
        return ans