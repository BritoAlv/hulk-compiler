# hulk-compiler

## A compiler for the Hulk Programming Language.

## Instructions:

Ejecutar *main.py* para ver la ayuda.

```bash
python3 main.py -r
```
El flag *-cg* puede ser substituido por :

- -l hasta el lexer.
- -p hasta el árbol de derivación.
- -a hasta el ast.
- -sa hasta el chequeo semántico.
- -cg hasta generación de código
- r ejecutar el código.

## Requirements

- Python3 + algunas librerías como Pickle, TermColor.
- SPIM (para ejecutar el mips generado por el compilador)