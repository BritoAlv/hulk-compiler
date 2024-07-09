BOOL_TYPE_ID = 0
NUMBER_TYPE_ID = 1
STR_TYPE_ID = 2
OBJ_TYPE_ID = 3

class VarData:
    def __init__(self, index : int, type : str = None) -> None:
        self.index = index
        self.type = type
        self.name = ""

class Context:
    def __init__(self) -> None:
        self.parent : Context = None
        self.children : list[Context] = []
        self.variables : dict[str, VarData] = {}

class FunctionData:
    def __init__(self, name = ""):
        self.type : str = None
        self.context : Context = Context()
        self.params : dict[str, VarData] = {}
        self.params_index : dict[int, str] = {}
        self.var_count = 0
        self.name = name

class TypeData:
    def __init__(self, id : int, name = "") -> None:
        self.id : int = id
        self.attributes : dict[str, VarData] = {}
        self.methods : dict[str, list[str]] = {} # Method name and it's associated assembly name
        self.inherited_offset = 1 # One word is reserved for object metadata (type in this case)
        self.ancestor : str = None
        self.descendants : list[str] = []
        self.name = name

class Environment:
    def __init__(self) -> None:
        self._functions : dict[str, FunctionData] = {}
        self._types : dict[str, TypeData] = {
            'Boolean': TypeData(BOOL_TYPE_ID, "Boolean"),
            'Number': TypeData(NUMBER_TYPE_ID, "Number"),
            'String': TypeData(STR_TYPE_ID, "String"),
            'Object': TypeData(OBJ_TYPE_ID, "Object")
        }
        
        self._types['Object'].descendants += ['Boolean', 'Number', 'String']
        self._types['Boolean'].ancestor = 'Object'
        self._types['Number'].ancestor = 'Object'
        self._types['String'].ancestor = 'Object'

    def get_function_data(self, function_name : str) -> FunctionData:
        if function_name not in self._functions:
            raise Exception(f"Function {function_name} is not declared")
         
        return self._functions[function_name]

    def add_function_data(self, function_name : str, function_data : FunctionData) -> None:
        if function_name in self._functions:
            raise Exception(f"Function {function_name} was already declared")
        
        self._functions[function_name] = function_data

    def add_type_data(self, type_name : str, type_data : TypeData) -> None:
        if type_name in self._types:
            raise Exception(f"Type {type_name} was already declared")
        
        self._types[type_name] = type_data

    def get_type_data(self, type_name : str) -> TypeData:
        if type_name not in self._types:
            raise Exception(f"Type {type_name} is not declared")
        
        return self._types[type_name]