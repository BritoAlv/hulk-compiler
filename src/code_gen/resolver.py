from code_gen.environment import Context, Environment, VarData

class Resolver:
    def __init__(self, environment : Environment) -> None:
        self._environment = environment
        self._params : dict[str, VarData] = None
        self._context : Context = None
        self._child_index : int = 0
        self.var_count = 0

    def start(self, func_name: str) -> None:
        self._params = self._environment.get_params(func_name)
        self._context = self._environment.get_context(func_name)
        self.var_count = self._environment.get_variables(func_name)
        self._child_index = 0

    def next(self) -> None:
        if self._context == None:
            raise Exception("Context is None")

        if self._child_index >= len(self._context.children):
            if self._context.parent == None:
                raise Exception("No more contexts to move on")
            
            self._child_index = self._context.parent.children.index(self._context) + 1
            self._context = self._context.parent
            return
        
        self._context = self._context.children[self._child_index]
        self._child_index = 0


    def resolve(self, var_name : str) -> VarData:
        if var_name in self._params:
            return self._params[var_name]
        
        if var_name in self._context.variables:
            return self._context.variables[var_name]
        
        temp_context = self._context.parent
        while(temp_context != None):
            if var_name in temp_context.variables:
                return self._context.variables[var_name]

            temp_context = temp_context.parent

        raise Exception("Variable was not declared")
    
    def get_func_type(self, func_name : str) -> str:
        return self._environment.get_type(func_name)
    
    def set_func_type(self, func_name : str, type : str) -> None:
        self._environment.add_type(func_name, type)