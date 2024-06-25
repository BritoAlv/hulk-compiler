from common.graph import Graph
from common.token_class import Token 
from common.parse_nodes.parse_tree import ParseTree
from common.parse_nodes.parse_node import ParseNode 

EPSILON = ""
EOF = "$"
ERROR = "ERROR"

class Grammar:
    # Parameters
    def __init__(self, 
                non_terminals: list[str], 
                terminals: list[str], 
                start_terminal: str, 
                productions: dict[str, list[list[str]]]) -> None:
        # Body
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.start_terminal = start_terminal 
        self.productions = productions

        # Initialize nullables
        # Nullables is a dictionary that gathers foreach non-terminal the information (boolean pair) about whether it has been verified through a nullable() call (first element of the tuple) and if so if it derives an epsilon (second element of the tuple)
        self._nullables: dict[str, tuple[bool, bool]] = {}
        for non_terminal in self.non_terminals:
            self._nullables[non_terminal] = (False, False)

        # Initialize derivation graph
        # Derivation graph is a graph data structure designed to avoid infinite derivations when calling nullable() or first_set()
        self._derivation_graph  = Graph()

        # Process nullables
        for non_terminal in self.non_terminals:
            self.nullable(non_terminal)

        # Initialize first sets
        # First sets is a dictionary that contains the first sets of all elements of the grammar (terminals and non-terminals). Notice that the values are pairs whose first elements are a booleans that assert if the set has been properly builded or not
        self._first_sets: dict[str, tuple[bool, list[str]]] = {}
        for element in (self.non_terminals + self.terminals):
            self._first_sets[element] = (False, [])

        # Reset derivation graph for first sets constructions
        self._derivation_graph = Graph()

        # Build first sets
        for element in (self.non_terminals + self.terminals):
            self.first_set(element)

        # Initialize follow sets
        self._follow_sets: dict[str, list[str]] = {}
        for non_terminal in self.non_terminals:
            self._follow_sets[non_terminal] = []

        # Build follow sets
        self._build_follow_sets()

        # Initialize LL(1) parsing table
        self.ll1_parsing_table: dict[str, list[list[str]]] = {}
        for non_terminal in self.non_terminals:
            self.ll1_parsing_table[non_terminal] = []
            for _ in self.terminals:
                self.ll1_parsing_table[non_terminal].append([])
            # Append one more list for the EOF right endmarker
            self.ll1_parsing_table[non_terminal].append([])

        # Build LL(1) parsing table
        self._build_ll1_parsing_table()

    def nullable(self, non_terminal: str) -> bool:
        # Check if non_terminal has already been verified
        if self._nullables[non_terminal][0]:
            return self._nullables[non_terminal][1]

        # Check each of the productions of non_terminal
        for production in self.productions[non_terminal]:
            # We'll assume it's indeed an epsilon production
            epsilon_production = True
            for product in production:
                # Verify the product is a terminal
                if product in self.terminals:
                    # The only valid terminal is epsilon itself
                    if product is EPSILON:
                        break
                    # If it's not epsilon discard production
                    epsilon_production = False
                    break

                # Since it was not a terminal, it's gotta be a non_terminal
                # Add it to the null graph
                pair = (non_terminal, product)
                self._derivation_graph.add(pair)

                # Check for a cycle to avoid an infinite derivation
                if(self._derivation_graph.is_cyclic()):
                    # If so, remove the edge and discard production
                    self._derivation_graph.remove(pair)
                    epsilon_production = False
                    break

                if not self.nullable(product):
                    # If the product does not derive epsilon, then remove the edge and discard the production
                    self._derivation_graph.remove(pair)
                    epsilon_production = False
                    break
            
            # If epsilon_production still true, it means that A -> epsilon or A -> B1, B2, ..., Bk where Bi is a non-terminal and Bi ->*epsilon for all i, 1 <= i <= k; therefore A ->*epsilon. (where A is the variable non_terminal)
            if epsilon_production:
                self._nullables[non_terminal] = (True, True)
                return True

        # A does not derive epsilon
        self._nullables[non_terminal] = (True, False)
        return False

    def first_set(self, element: str) -> list[str]:
        # Verify in first sets dictionary
        if(self._first_sets[element][0]):
            return self._first_sets[element][1]
        
        # If element is a terminal then its first set is the set containing it 
        first_set: list[str] = []
        if element in self.terminals:
            first_set.append(element)
            self._first_sets[element] = (True, first_set)
            return first_set
        
        # If it's not a terminal
        for production in self.productions[element]:
            for product in production:
                # A -> B1,B2,...,Bk
                # First(B1) ⊆ First(A) and if B1 ->*epsilon, then First(B2) ⊆ First(A), and if B2 ->*epsilon, then First(B3) ⊆ First(A), ..., and so on.

                # If it's a non terminal add edge to null graph
                if product in self.non_terminals and not self._derivation_graph.contains_edge((element, product)):
                    self._derivation_graph.add((element, product))
                
                # Verify null graph is cyclic, if so remove the edge and discard product
                if self._derivation_graph.is_cyclic():
                    self._derivation_graph.remove((element, product))
                    break

                for terminal in self.first_set(product):
                    if terminal not in first_set:
                        first_set.append(terminal)

                # A terminal cannot be nullable. In case it's not a terminal, verify it's nullability
                if product in self.terminals or not self.nullable(product):
                    break

        self._first_sets[element] = (True, first_set)
        return first_set

    # First(X1, X2, ..., Xk) = First(X1) - {epsilon}, and if epsilon ∈ First(X1), then also add First(X2) - {epsilon}, and if epsilon ∈ First(X1) and First(X2), then also add First(X3) - {epsilon}, and so on and so forth. Notice that if epsilon ∈ Xi for all i, 1<=i<=k then epsilon ∈ First(X1, X2, ...., Xk)
    def list_first_set(self, elements: list[str]) -> list[str]:
        first_set: list[str] = []
        for element in elements:
            process_next = False
            for literal in self.first_set(element):
                if literal is not EPSILON:
                    first_set.append(literal)
                else:
                    process_next = True

            if(process_next and element is elements[len(elements) - 1]):
                first_set.append(EPSILON)

            if not process_next:
                break

        return first_set
    
    def follow_set(self, non_terminal: str) -> list[str]:
        return self._follow_sets[non_terminal]
    
    def _build_follow_sets(self) -> None:
        self._follow_sets[self.start_terminal].append(EOF)

        while(True):
            changes_ocurred = False

            for non_terminal in self.non_terminals:
                for production in self.productions[non_terminal]:
                    # Index of product in productions
                    index = 0
                    for product in production:
                        # If it's a terminal continue
                        if product not in self.non_terminals:
                            index += 1
                            continue
                            
                        # Get the first set of the suffix starting after product 
                        suffix_first_set = self.list_first_set(production[index+1:len(production)])
                        # Remove epsilon from suffix's first set
                        epsilon_in_suffix = False
                        if EPSILON in suffix_first_set:
                            suffix_first_set.remove(EPSILON)
                            epsilon_in_suffix = True

                        # Add suffix's first set's elements into product's follow set
                        changes_ocurred = self._add_to_follow(product, suffix_first_set) or changes_ocurred

                        # If suffix's first set contained epsilon or product is the last one of production
                        if epsilon_in_suffix or index is (len(production) - 1):
                            changes_ocurred = self._add_to_follow(product, self._follow_sets[non_terminal]) or changes_ocurred

                        # Increase index for the next product
                        index += 1 
                        
            if not changes_ocurred:
                break

    def _add_to_follow(self, non_terminal: str, set: list[str]) -> bool:
        changes_ocurred = False
        for literal in set:
            if literal not in self._follow_sets[non_terminal]:
                self._follow_sets[non_terminal].append(literal)
                changes_ocurred = True
        return changes_ocurred
    
    def _build_ll1_parsing_table(self) -> None:
        for non_terminal in self.non_terminals:
            for production in self.productions[non_terminal]:
                for first_terminal in self.list_first_set(production):
                    first_index = self.terminals.index(first_terminal)
                    self._insert_into_parsing_table(non_terminal, first_index, production)

                    if first_terminal is EPSILON:
                        for follow_terminal in self.follow_set(non_terminal):
                            if follow_terminal is EOF:
                                eof_index = len(self.ll1_parsing_table[non_terminal]) - 1
                                self._insert_into_parsing_table(non_terminal, eof_index, production)
                            else:
                                follow_index = self.terminals.index(follow_terminal)
                                self._insert_into_parsing_table(non_terminal, follow_index, production)

    def _insert_into_parsing_table(self, non_terminal: str, terminal_index: int, value: list[str]):
        # Verify entry is still empty
        if len(self.ll1_parsing_table[non_terminal][terminal_index]) == 0:
            self.ll1_parsing_table[non_terminal][terminal_index]= value
        else:
            raise RuntimeError("Grammar is not LL(1) more than one value per table entry")
        
    def parse(self, input: list[Token]) -> ParseTree:
        parse_tree = ParseTree(ParseNode(self.start_terminal))

        # Start on the first character
        input_index = 0
        # Add EOF -> Start Terminal to the parse stack
        stack: list[ParseNode] = [ParseNode(EOF), parse_tree.root]
        # While parse stack is not empty
        while len(stack) > 0:
            top = stack[len(stack) - 1]
            token_type = input[input_index].type

            # If the top of the stack is a non-terminal
            if top.value in self.non_terminals:
                # Assume token_type is an EOF, whose index is the last one by convention
                terminal_index = len(self.ll1_parsing_table[top.value]) - 1
                # If it's indeed not an EOF, then find its index
                if token_type != EOF:
                    terminal_index = self.terminals.index(token_type)

                derivation: list[ParseNode] = []
                for element in self.ll1_parsing_table[top.value][terminal_index]:
                    child_node = ParseNode(element)
                    child_node.parent = top
                    top.children.append(child_node)
                    derivation.append(child_node)
                
                # If there is a derivation add it to the stack (if it's not epsilon)
                if len(derivation) > 0:
                    stack.pop()
                    if not(len(derivation) == 1 and derivation[0].value == EPSILON):
                        derivation.reverse()
                        stack.extend(derivation)
                # If there's no derivation, then there have been a parsing error
                else:
                    raise RuntimeError("There have been a parsing error")
            # If the top of the stack is a terminal
            else:
                # Match it
                if top.value == token_type:
                    stack.pop()
                    # Move forward on the input
                    input_index += 1
                # If it didn't match there have been a parsing error
                else:
                    raise RuntimeError("There have been a parsing error")
        return parse_tree