"""

Regular Expressions follows this grammar:

A => B X
X => +A | epsilon
B => P Y
Y => B | epsilon
C => chZ | (E)Z
Z => * | ? | epsilon 

"""