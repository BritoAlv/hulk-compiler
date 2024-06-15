from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *

EOF = "$"

class ParsingTable:
    def __init__(self, total_states: int):
        self.table_input = [{} for i in range(0, total_states)]
        self.table_nonterminals = [{} for i in range(0, total_states)]

    def add_reduce_transition(self, st: int, terminal: str, key: str, len: int):
        if terminal in self.table_input[st]:
            if self.table_input[st][terminal] == "s":
                print(
                    "Grammar is not LR contains a shift reduce conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal] == "r":
                print(
                    "Grammar is not LR contains a reduce reduce conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal] == "a":
                print(
                    "Grammar is not LR, this state",
                    st,
                    " with therminal",
                    terminal,
                    "is supposed to be AC, not reduce",
                )
            print("BOOM")
            return
        else:
            self.table_input[st][terminal] = ("r", key, len)

    def add_shift_transition(self, st: int, terminal: str, new_state: int):
        if terminal in self.table_input[st]:
            if (
                self.table_input[st][terminal] == "s"
                and self.table_input[st][1] != new_state
            ):
                print(
                    "Grammar is not LR contains a shift shift conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
                print("This is not supposed to happen")
            if self.table_input[st][terminal] == "r":
                print(
                    "Grammar is not LR contains a shift reduce conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal] == "a":
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
            if self.table_input[st][terminal] == "s":
                print(
                    "Grammar is not LR contains a shift accept conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
                print("This is not supposed to happen")
            if self.table_input[st][terminal] == "r":
                print(
                    "Grammar is not LR contains a reduce accept conflict at state",
                    st,
                    "with terminal",
                    terminal,
                )
            if self.table_input[st][terminal] == "a":
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

    def parse(self, inputTokens: list[Token]) -> ParseTree:
        stackStates = []
        stackStates.append(0)
        stackParse: list[ParseNode] = []
        cr = 0
        while True:
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
                stackParse.append(nodeResult)
                assert stackParse[-1].value in self.table_nonterminals[stackStates[-1]]
                stackStates.append(
                    self.table_nonterminals[stackStates[-1]][stackParse[-1].value]
                )

    def __str__(self):
        header = "State".ljust(20) + "".join([x.ljust(20) for x in terminals]) + "".join([x.ljust(20) for x in non_terminals])
        rows = [
            str(i).ljust(20)
            + "".join(
                [
                    str(self.table_input[i][x]).ljust(20) if x in self.table_input[i] else "".ljust(20)
                    for x in terminals
                ]
            )
            + "".join(
                [
                    (
                        str(self.table_nonterminals[i][x]).ljust(20)
                        if x in self.table_nonterminals[i]
                        else "".ljust(20)
                    )
                    for x in non_terminals
                ]
            )
            for i in range(0, len(self.table_input))
        ]
        return header + "\n" + "\n".join(rows)

pt = ParsingTable(8)
terminals = ["a", "b", "c", "$"]
non_terminals = ["S"]
for nont in terminals:
    pt.add_accept_transition(1, nont)

pt.add_nonterminal_transition(0, "S", 1)
pt.add_nonterminal_transition(2, "S", 4)

for nont in terminals:
    pt.add_reduce_transition(5, nont, "S", 2)
    pt.add_reduce_transition(6, nont, "S", 3)
    pt.add_reduce_transition(7, nont, "S", 3)

pt.add_shift_transition(0, "a", 2)
pt.add_shift_transition(0, "b", 3)

pt.add_shift_transition(2, "a", 2)
pt.add_shift_transition(2, "b", 3)

pt.add_shift_transition(3, "c", 5)

pt.add_shift_transition(4, "b", 6)
pt.add_shift_transition(4, "c", 7)

print(pt)

tree = pt.parse([Token(x) for x in [*list("bc"), EOF]])
tree.root.print([], 0, False)

tree = pt.parse([Token(x) for x in [*list("abcc"), EOF]])
tree.root.print([], 0, False)

tree = pt.parse([Token(x) for x in [*list("aaabcccc"), EOF]])
tree.root.print([], 0, False)

tree = pt.parse([Token(x) for x in [*list("aabccc"), EOF]])
tree.root.print([], 0, False)