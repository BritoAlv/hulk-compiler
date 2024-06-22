class VarData:
    def __init__(self, index : int, type : str = None) -> None:
        self.index = index
        self.type = type

class Context:
    def __init__(self) -> None:
        self.parent : Context = None
        self.children : list[Context] = []
        self.variables : dict[str, VarData] = {}

class FunctionData:
    def __init__(self):
        self.type : str = None
        self.context : Context = None
        self.params : dict[str, VarData] = {}
        self.var_count = 0

class Environment:
    def __init__(self) -> None:
        self._functions : dict[str, FunctionData] = {}

    def add_function(self, func_name : str) -> None:
        if func_name in self._functions:
            raise Exception(f"Function {func_name} was already declared")
        
        self._functions[func_name] = FunctionData()
    
    def get_context(self, func_name : str) -> Context:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._functions[func_name].context
    
    def add_context(self, func_name : str, context : Context) -> None:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")
        
        self._functions[func_name].context = context
    
    def get_params(self, func_name: str) -> dict[str, VarData]:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._functions[func_name].params
    
    def get_variables(self, func_name: str) -> int:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._functions[func_name].var_count
    
    def add_variables(self, func_name : str, count : int) -> None:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")
        
        self._functions[func_name].var_count = count

    def add_type(self, func_name : str, type : str) -> None:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")

        self._functions[func_name].type = type

    def get_type(self, func_name : str) -> str:
        if func_name not in self._functions:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._functions[func_name].type