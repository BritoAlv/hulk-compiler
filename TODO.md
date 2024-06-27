## Semantic Requirements:
- Length of args in calls must match length of params in methods/functions definition
- Expression after **in** in for expressions must be of type **Iterable**
- Resolve types of functions and arguments

## CodeGen Requirements:
- Print floats as floats
- Compare strings (equality) char by char

## Lexer and Parser Error Handling:
- how get lexer tell errors.

# Testing:

## Find Algorithm That Given Grammar Generates valid sentences of it to be able to test ast converter, semantic analysis and code generation.

This can be done in the following stupid way:
    - generate a random number $N$ that will be the number of tokens of the code .
    - generate random $N$ tokens, but given the type of the token is needed to find an string that matches the regular expression of the token. ( we can precompute this, ie, find an Algorithm that given a regular expression find secuences that match it and store some valid ones.)
    - pass the array of generated tokens to the parser if it succeeds store that test.