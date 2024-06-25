class Context():
    def __init__(self , parent = None) -> None:
        self.parent = parent
        self.dict = {}
        self.function = {}

    def is_defined(self, var) -> bool:
        return self.dict[var] or (self.parent != None and self.parent.is_defined(var))
    
    def is_defined_func(self, func, args) -> bool:
        if self.function[func] and self.function[func] == args:
            return True
        return (self.parent != None and self.parent.is_defined_func(func, args))
    
    def define(self, var) -> bool:
        if self.is_defined(var):
            return False
        self.dict[var] = True
        return True
    
    def define_func(self, var, args) -> bool:
        if self.is_defined_func(var, args):
            return False
        self.function[var] = True
        return True
    
    def create_child_context(self):
        return Context(self)