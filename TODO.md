## Semantic Requirements:
- errors are wrong due to corrupt ast.
- for to while ruins error report.
- explicit vector corruption ruins semantic check.
- handle better push and pop of type determiner.
- private attributes are missing.
- semantic analysis should be done before corrupting the ast.
## CodeGen Requirements:
- Compare strings (equality) char by char.
- RunTime Error for overflow.
- Implement Random function.
- Implement Vectors using lists instead of LinkedList.
- Optimize assembly dynamic dispatch.