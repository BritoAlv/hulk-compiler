from parsing.parser_generator_lr.grammarLR1 import GrammarLR1

def gramophoneSyntaxParser( inputTokens : str, name : str) -> GrammarLR1:
    non_terminals = []
    terminals = []
    start_symbol = ""
    productions = {}
    
    def add_symbol( symbol : str):
        symbol = symbol.strip()
        if len(symbol)  == 0:
            pass
        elif symbol[0].islower():
            if symbol not in terminals:
                terminals.append(symbol)
        else:
            if symbol not in non_terminals:
                non_terminals.append(symbol)
                productions[symbol] = []
        return symbol


    lines = inputTokens.split("\n")
    for line in lines:
        if len(line) > 0:
            line = line.strip() 
            line = line[:-1]
            parts = line.split("->")
            non_terminal = add_symbol(parts[0])
            if start_symbol == "":
                start_symbol = non_terminal
            productionsLine = parts[1].split("|")
            for prod in productionsLine:
                prod = prod.strip().split(" ")
                prod_to_add = []
                for symbol in prod:
                    symbol = add_symbol(symbol)
                    if len(symbol) > 0:
                        prod_to_add.append(symbol)
                productions[non_terminal].append(prod_to_add)

    return GrammarLR1(name, non_terminals, terminals, start_symbol, productions)