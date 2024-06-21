class Context:
    def __init__(self) -> None:
        self.parent : Context = None
        self.children : list[Context] = []
        self.variables : dict[str, int] = {}

class Environment:
    def __init__(self) -> None:
        self._scopes : dict[str, Context] = {}
        self._params : dict[str, dict[str, int]] = {}
        self._var_count : dict[str, int] = {}

    def add(self, func_name : str) -> None:
        if func_name in self._scopes:
            raise Exception(f"Function {func_name} was already declared")
        
        self._scopes[func_name] = None
        self._params[func_name] = {}
        self._var_count[func_name] = 0
    
    def get_context(self, func_name : str) -> Context:
        if func_name not in self._scopes:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._scopes[func_name]
    
    def get_params(self, func_name: str) -> dict[str, str]:
        if func_name not in self._params:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._params[func_name]
    
    def get_variables(self, func_name: str) -> int:
        if func_name not in self._var_count:
            raise Exception(f"Function {func_name} is not declared")
        
        return self._var_count[func_name]
    
    def add_variables(self, func_name : str, count : int) -> None:
        if func_name not in self._var_count:
            raise Exception(f"Function {func_name} is not declared")
        
        self._var_count[func_name] = count

    def add_context(self, func_name : str, context : Context) -> None:
        if func_name not in self._scopes:
            raise Exception(f"Function {func_name} is not declared")
        
        self._scopes[func_name] = context