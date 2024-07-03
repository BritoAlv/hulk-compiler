## Semantic Requirements:
- Length of args in calls must match length of params in methods/functions definition
- Expression after **in** in for expressions must be of type **Iterable**
- Resolve types of functions and arguments
- After is, as should follow type names.

## CodeGen Requirements:
- Print floats as floats
- Compare strings (equality) char by char
- Handle method dispatch when object
- Is returns true on ancestors
- Remove type inference during CodeGen

## Lexer and Parser Error Handling:
- how get lexer tell errors.
- lexer printing errors have bugs.

# Testing:

## Exceptions should be logged and not raised.

#
- infer parameter types.
- for each protocol know which type implements it.
- infer type of functions.
- keep track of constructors. semantic check for constructors. type of params in the constructors.
- covariance and contravariance.