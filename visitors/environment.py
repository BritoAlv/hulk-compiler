class Environment:
    def __init__(self, environment = None):
        self.enclosing = environment
        self.variables = {}

    def get_distance(self, distance):
        act = self
        while distance > 0:
            act = act.enclosing
            distance -= 1
        return act

    def define(self, distance, name, value):
        use = self.get_distance(distance)
        if name in use.variables:
            raise Exception("Variable " + name + " already exists")
        use.variables[name] = value

    def get(self, distance, name):
        use = self.get_distance(distance)
        if name not in use.variables:
            if use.enclosing == None:
                raise Exception("Variable " + name + " is not defined")
            return use.enclosing.get(name)
        return use.variables[name]
    
    def set(self, distance, name, value):
        use = self.get_distance(distance)
        if name not in use.variables:
            if use.enclosing == None:
                raise Exception("Variable " + name + " is not defined")
            return use.enclosing.set(name, value)
        use.variables[name] = value