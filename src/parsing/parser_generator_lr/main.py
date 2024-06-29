from common.token_class import Token
from parsing.parser_generator_lr.grammarLR1 import GrammarLR1
from parsing.parser_generator_lr.utils import gramophoneSyntaxParser


gr = GrammarLR1(
    name = "test2",
    non_terminals=["S", "A", "B"],
    terminals=["a", "b", "c"],
    start_symbol="S",
    productions={
        "S": [["A", "a", "B", "b"]],
        "A": [["c"]],
        "B": [[]]
    }
)
ptable = gr.BuildParsingTable(reuse=False)
print(ptable)

inputStr = "cdab"

tree = ptable.parse(
    [Token(x,x, 0, i) for (i, x) in enumerate([*list(inputStr), "$"])], inputStr 
)

tree.root.print([], 0, False)