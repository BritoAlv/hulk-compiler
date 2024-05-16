El evaluador depende de el resolver para encontrar las variables, más aún se puede leer el árbol y precomputar donde estarían las variables, esto es la tarea del resolver, le da esa información a el Evaluador. 

Ambos poseen contratos comunes ( no se pueden hacer por separado ) como cuando:
    - cuando se ejecuta un bloque de código se crea un environment nuevo, y una variable accedida siempre se refiere a la que está en el innermost en el momento en que es declarada.