from common.token_class import Token
from parsing.parser_generator_lr.grammarLR1 import GrammarLR1
from parsing.parser_generator_lr.utils import gramophoneSyntaxParser


inputTest = """

S -> a S b a | .

"""

gr = gramophoneSyntaxParser(inputTest, "basicEnough")

table = gr.BuildParsingTable(False)
table = gr.BuildParsingTable()

print(table)

tree = table.parse([Token(x, x, 0,0 ) for x in "aababa$"]) # aababa 

tree.root.print([0], 0, True)