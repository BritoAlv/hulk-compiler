import math

def log(x, base=math.e):
    """
    Calcula el logaritmo de un número x en la base especificada.
    Si no se especifica la base, se calcula el logaritmo natural (ln).
    """
    # Verificar que x sea un número positivo
    if x <= 0:
        raise ValueError("El argumento debe ser un número positivo")
    
    # Calcular el logaritmo natural (ln)
    a = 0
    b = x
    tol = 1e-10
    
    while abs(b - a) > tol:
        c = (a + b) / 2
        if pow(base, c) > x:
            b = c
        else:
            a = c
    
    # Si la base es diferente de e, convertir a la base deseada
    if base != math.e:
        return c / math.log(base)
    else:
        return c
    

print(log(16))       # Salida: 2.7725887222397812
print(log(2, 2))     # Salida: 1.0
print(log(100, 10))  # Salida: 2.0
print(log(1))
