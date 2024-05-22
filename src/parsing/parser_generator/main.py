from parsing.parser_generator.grammar import Grammar, EPSILON, EOF
from common.token_class import Token

non_terminals = ['term', 'rterm', 'factor', 'rfactor', 'primary']
terminals = [EPSILON, 'plus', 'minus', 'star', 'div', 'rparen', 'lparen', 'num'] 
start_symbol = "term"
productions = {
    "term": [['factor', "rterm"]],
    'rterm': [['plus', 'term'], ['minus', 'term'], [EPSILON]],
    'factor': [['primary', 'rfactor']],
    'rfactor': [['star', 'factor'], ['div', 'factor'], [EPSILON]],
    'primary': [['num'], ['lparen', 'term', 'rparen']]
}

g = Grammar(non_terminals, terminals, start_symbol, productions)

num = Token('num', '25', 0, 0)
plus = Token('plus', '+', 0, 0)
star = Token('star', '*', 0, 0)
div = Token('div', '/', 0, 0)
minus = Token('minus', '-', 0, 0)
lparen = Token('lparen', '(', 0, 0)
rparen = Token('rparen', ')', 0, 0)
eof = Token(EOF, '\0', 0, 0)

parse_tree = g.parse([num, star, lparen, num, plus, num, rparen, eof])

parse_tree.root.print([0], 0, True)