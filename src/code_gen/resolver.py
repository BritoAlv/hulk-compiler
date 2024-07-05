from code_gen.environment import Context, Environment, FunctionData, TypeData, VarData

class Resolver:
    def __init__(self, environment : Environment) -> None:
        self._environment = environment
        self._params : dict[str, VarData] = None
        self._context : Context = None
        self._child_index : int = 0

    def start(self, func_name: str) -> None:
        func_data = self._environment.get_function_data(func_name)

        self._params = func_data.params
        self._context = func_data.context
        self._child_index = 0

    def resolve_types(self):
        return self._environment._types.keys()

    def resolve_functions(self):
        return self._environment._functions.keys()

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


    def resolve_var_data(self, var_name : str) -> VarData:
        if var_name in self._context.variables:
            return self._context.variables[var_name]
        
        temp_context = self._context.parent
        while(temp_context != None):
            if var_name in temp_context.variables:
                return temp_context.variables[var_name]

            temp_context = temp_context.parent

        if var_name in self._params:
            return self._params[var_name]

        raise Exception("Variable was not declared")
    
    def resolve_function_data(self, func_name : str) -> FunctionData:
        return self._environment.get_function_data(func_name)

    def resolve_type_data(self, type_name : str) -> TypeData:
        return self._environment.get_type_data(type_name)
    
    def resolve_lowest_common_ancestor(self, type_1 : str, type_2 : str) -> str:
        BASIC_TYPES = ['Number', 'String', 'Boolean', "Object"]
        
        if type_1 == type_2:
            return type_1
        
        if type_1 in BASIC_TYPES or type_2 in BASIC_TYPES:
            return "Object"

        type_data_1 = self._environment.get_type_data(type_1)

        if type_2 in type_data_1.descendants:
            return type_1
        
        if type_data_1.ancestor == None:
            return "Object"
        
        return self.resolve_lowest_common_ancestor(type_data_1.ancestor, type_2)