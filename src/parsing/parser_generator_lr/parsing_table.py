from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *

EOF = "$"


        

class ParsingTable:
    def __init__(
        self,
        total_states: int,
        terminals: list[str],
        non_terminals: list[str],
        productions: dict[str, list[list[str]]] | None = None,
        attributed_productions=None,
    ):
        self.table_input: list[dict] = [{} for i in range(0, total_states)]
        self.table_nonterminals = [{} for i in range(0, total_states)]
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions
        self.attributed_productions = attributed_productions
        
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

    def parse(self, inputTokens: list[Token]) -> ParseTree:
        stackStates = []
        stackStates.append(0)
        stackParse: list[ParseNode] = []
        cr = 0
        while True:
            if inputTokens[cr].type not in self.table_input[stackStates[-1]]:
                print(
                    "Parsing error, no transition for",
                    inputTokens[cr].type,
                    "at state",
                    stackStates[-1],
                )
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
            if len(self.productions[value][i]) == len(tree.children): # type: ignore
                flag = True
                for j in range(0, len(tree.children)):
                    if (tree.children[j].value != self.productions[value][i][j]):
                        flag = False
                if flag:
                    return i

    def convertAst(self, tree: ParseNode):
        body = tree.children
        s = []

        for i in range(0, len(body) + 1):
            s.append(None)

        for i, node in enumerate(body, 1):
            if node != None:
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