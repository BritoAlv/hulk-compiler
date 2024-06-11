from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *

EOF = "$"
ERROR = "ERROR"
DUMMY = "'"


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
        self.terminals = terminals + [EOF]
        self.start_terminal = start_terminal
        self.productions = productions
        productions[DUMMY] = [[self.start_terminal, EOF]]
        self.automaton = self.build_lr0_automaton()

    def check_conflicts(self) -> bool:
        for st in self.automaton.accepting_states:
            for z in range(0, len(self.automaton.alphabet)):
                if self.automaton.table[z][st] != []:
                    print(
                        "Reduce / Shift Conflict at state: "
                        + str(st)
                        + " with symbol: "
                        + self.automaton.alphabet[z]
                    )
                    return False
            if len(self.automaton.additional_info[st]) > 1:
                print("Reduce / Reduce Conflict at state: " + str(st))
                nodeResult = ParseNode("ERROR")
                nodeResult.token = Token("ERROR", ERROR, 0, 0)
                return ParseTree(nodeResult)

    def parse(self, input: list[Token]) -> ParseTree:
        cr = 0
        stackStates = [self.automaton.start_state]
        stackParse: list[Token | ParseNode] = [input[0]]
        while True:
            print("Algorithm LR(0) Track")
            next = self.automaton.next_state(
                (
                    stackParse[-1].type
                    if type(stackParse[-1]) == Token
                    else stackParse[-1].value
                ),
                stackStates[-1],
            )
            print("States: ", stackStates)
            print("Stack Parsed:", end=" ")
            for el in stackParse:
                if type(el) == Token:
                    print(el.type, end=" ")
                else:
                    print(el.value, end=" ")
            print("")
            print("current is", stackStates[-1], "next is", next)

            if type(stackParse[-1]) == ParseNode and stackParse[-1].value == DUMMY:
                return ParseTree(stackParse[-1].children[-1])

            if next == -1:
                print(
                    "Syntax error due to : there is no transition from: "
                    + str(stackStates[-1])
                    + " with token: "
                    + input[cr].type
                )
                return ParseTree(ParseNode("ERROR"))
            stackStates.append(next)
            if next not in self.automaton.accepting_states:
                print("Shift")
                cr += 1
                if(cr >= len(input)):
                    print("All the input was consumed but parsing has not ended yet")
                    return ParseTree(ParseNode("ERROR"))
                stackParse.append(input[cr])
            else:
                print("Reduce")
                prod = self.automaton.additional_info[next][0][1]
                print("Production to reduce is", prod)
                len_pop = len(prod)
                print("stackStates after reduce", stackStates)
                flag = False
                for key in self.productions.keys():
                    if prod in self.productions[key]:
                        nodeResult = ParseNode(key)
                        nodeResult.token = Token(key, key, 0, 0)
                        for _ in range(0, len(prod)):
                            next = stackParse.pop()
                            if type(next) == Token:
                                nextt = ParseNode(next.type)
                                nextt.token = next
                                next = nextt
                            nodeResult.children.append(next)
                            stackStates.pop()
                        stackParse.append(nodeResult)
                        flag = True
                        break
                if not flag:
                    print("Error: Production not found")
                    nodeResult = ParseNode("ERROR")
                    nodeResult.token = Token("ERROR", ERROR, 0, 0)
                    return ParseTree(nodeResult)
            print("---------------------")

    def build_lr0_automaton(self):
        states_additional = []
        transitions = []
        mapped: list[tuple[int, list[str]]] = []

        def add_new_state(st: tuple[int, list[str]]):
            mapped.append(st)
            states_additional.append(st)

        def map_state(st: tuple[int, list[str]]) -> int:
            return mapped.index(st)

        def add_transition(
            letter: str, source: tuple[int, list[str]], dest: tuple[int, list[str]]
        ):
            transitions.append([map_state(source), map_state(dest), letter])

        accepting_states = []

        for key in self.productions.keys():
            add_new_state((0, [key]))  # add [. S]
        for key in self.productions.keys():
            for prod in self.productions[key]:
                for i in range(0, len(prod) + 1):
                    new_st = (i, prod)
                    add_new_state(new_st)
                    if i > 0:
                        add_transition(prod[i - 1], (i - 1, prod), (i, prod))
                    else:
                        add_transition(EPSILON, (0, [key]), (0, prod))

                    if i < len(prod) and prod[i] in self.non_terminals:
                        add_transition(EPSILON, new_st, (0, [prod[i]]))
                    elif i == len(prod):
                        if map_state(new_st) not in accepting_states:
                            accepting_states.append(map_state(new_st))
        start_state = map_state((0, [DUMMY]))
        total_states = len(mapped)
        alphabet = self.non_terminals + self.terminals + [EPSILON]
        table = [[] for z in range(0, len(alphabet))]
        for z in range(0, len(alphabet)):
            for j in range(0, total_states):
                table[z].append([])

        for tr in transitions:
            table[alphabet.index(tr[2])][tr[0]].append(tr[1])

        additional_info = [[] for i in range(0, total_states)]
        for st in mapped:
            additional_info[map_state(st)].append(st)

        nfa = NFA(
            start_state,
            total_states,
            alphabet,
            accepting_states,
            table,
            additional_info,
            False,
        )
        dfa = nfa.ConvertNFA_DFA()
        return dfa


gr = Grammar(
    non_terminals=["E", "T", "F"],
    terminals=["(", ")", "id", "+", "*"],
    start_terminal="E",
    productions={
        "E": [["E", "+", "T"], ["T"]],
        "T": [["T", "*", "F"], ["F"]],
        "F": [["id"], ["(", "E", ")"]]
    }
)

tree = gr.parse(
    [
        Token("id", "a", 0, 0),
        Token("+", "+", 0, 0),
        Token("id", "b", 0, 0),
        Token(EOF, EOF, 0, 0)
    ]
)
tree.root.print([], 0, False)