class Environment:
    def __init__(self, environment = None):
        self.enclosing = environment
        self.variables = {}

    def define(self, name, value):
        if name in self.variables:
            raise Exception("Varaible " + name + " already exists")
        self.variables[name] = value

    def get(self, name):
        if name not in self.variables:
            if self.enclosing == None:
                raise Exception("Variable " + name + " is not defined")
            return self.enclosing.get(name)
        return self.variables[name]
    
    def set(self, name, value):
        if name not in self.variables:
            if self.enclosing == None:
                raise Exception("Variable " + name + " is not defined")
            return self.enclosing.set(name, value)
        self.variables[name] = value