# hulk-compiler

## Instructions:

Ejecutar *main.py* para ver la ayuda.

```bash
python3 main.py -cg < program.hulk
python3 main.py -cg << EOF
# your HULK code
42;
# EOF
```
El flag *-cg* puede ser substituido por :

- -l hasta el lexer.
- -p hasta el árbol de derivación.
- -a hasta el ast.
- -sa hasta el chequeo semántico.
- -cg hasta generación de código.

## Requirements

- Python3 y la librería *pickle*