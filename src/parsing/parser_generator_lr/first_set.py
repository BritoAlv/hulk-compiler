from parsing.parser_generator.graph import Graph
from common.token_class import Token 
from common.parse_nodes.parse_tree import ParseTree
from common.parse_nodes.parse_node import ParseNode 

class First_Set_Calculator:
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
        self.EPSILON = ""
        

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
                    if product is self.EPSILON:
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
                if product in self.non_terminals:
                    self._derivation_graph.add((element, product))
                
                # Verify null graph is cyclic, if so remove the edge and discard product
                if self._derivation_graph.is_cyclic():
                    self._derivation_graph.remove((element, product))
                    continue

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
                if literal is not self.EPSILON:
                    first_set.append(literal)
                else:
                    process_next = True

            if(process_next and element is elements[len(elements) - 1]):
                first_set.append(self.EPSILON)

            if not process_next:
                break

        return first_set