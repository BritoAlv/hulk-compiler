from common.ErrorLogger.ErrorLogger import ErrorLogger
from common.ast_nodes.expressions import *
from common.ast_nodes.expressions import VectorGetNode
from common.ast_nodes.statements import *
from common.visitor import Visitor

class ComputedValue:
    def __init__(self, type, value = None) -> None:
        self.type = type
        self.value = value 

class Vector:
    def __init__(self, values) -> None:
        self.values = values
    def __str__(self) -> str:
        return "Vector"
    
class Type:
    def __init__(self, name, args) -> None:
        self.name = name
        self.attribute = []
        self.method = []
        self.args = args

    def add_args(self, args):
        for (i, j) in args:
            self.args.append(Attribute(i, j))

    def get_attribute(self, name):
        for i in self.attribute:
            if i.name == name:
                return i
        return None
    
    def get_method(self, name, args):
        for i in self.method:
            if i.name == name :
                return i
        return None  
    
    def get_method_whithout_params(self, name):
        for i in self.method:
            if i.name == name:
                return i
        return None     

    def define_attribute(self, name, type):
        if self.get_attribute(name) != None:
            return False
        self.attribute.append(Attribute(name, type))

    def define_method(self, name, return_type, args):
        if self.get_method(name, args) != None:
            return False
        args_type = []
        for (i, j) in args:
            args_type.append(Attribute(i.lexeme, j.lexeme if j != None else None))
        self.method.append(Method(name, return_type, args_type))

class Attribute:
    def __init__(self, name, itype) -> None:
        self.name = name
        self.type = itype

class Method:
    def __init__(self, name, return_type, args) -> None:
        self.name = name
        self.type = return_type
        self.args = args

class ContextValue:
    def __init__(self, type, value = None) -> None:
        self.value = value
        self.type = type

class ContextLower():
    def __init__(self, parent = None) -> None:
        self.parent = parent
        self.dict = {}
        self.method = []

    def is_defined(self, var) -> bool:  # da o False si no existe o el valor del dict
        return self.dict.get(var) != None or (self.parent != None and self.parent.is_defined(var))
   
    def is_defined_local(self, var) -> bool:  # da o False si no existe o el valor del dict
        return self.dict.get(var) != None
    
    def is_defined_func(self, name, args) -> bool:
        for i in self.method:
            if i.name == name:
                return i
        return self.parent.is_defined_func(name, args) if self.parent != None else None
    
    def is_defined_func_whithout_params(self, name) -> bool:
        for i in self.method:
            if i.name == name:
                return True
        return (self.parent != None and self.parent.is_defined_func_whithout_params(name))
    
    def get(self, name):
        return self.dict.get(name) or (self.parent != None and self.parent.get(name))

    def define(self, var, type, value = None) -> bool:
        if self.dict.get(var) != None:
            return False
        self.dict[var] = ContextValue(type, value)
        return True
    
    def remove_define(self, var) -> bool:
        if self.is_defined(var):
            self.dict.pop(var)
    
    def define_func(self, name, return_type, args) -> bool:
        if self.is_defined_func(name, args) != None:
            return False
        args_type = []
        for (i, j) in args:
            args_type.append(Attribute(i.lexeme, j.lexeme if j != None else None))
        self.method.append(Method(name, return_type, args_type))

    def create_child_context(self):
        return ContextLower(self)
        
class Context():
    def __init__(self , parent = None) -> None:
        self.context_lower : ContextLower = ContextLower()
        self.types : list[Type] = []

    def is_defined(self, var) -> bool:
        return self.context_lower.is_defined(var)
    
    def is_defined_local(self, var) -> bool:
        return self.context_lower.is_defined_local(var)
    
    def is_defined_func(self, func, args) -> bool:
        return self.context_lower.is_defined_func(func, args)

    def is_defined_func_whithout_params(self, func) -> bool:
        return self.context_lower.is_defined_func_whithout_params(func)


    def get(self, name):
        return self.context_lower.get(name)     
    
    def set(self, name, type_new):
        self.context_lower.dict[name] = type_new

    def define(self, var, type = None, value = None) -> bool:
        return self.context_lower.define(var, type, value)
    
    def remove_define(self, var) -> bool:
        return self.context_lower.remove_define(var)
    
    def define_func(self, var, return_type, args) -> bool:
        return self.context_lower.define_func(var, return_type, args)
    
    def create_child_context(self):
        self.context_lower = self.context_lower.create_child_context()
    
    def remove_child_context(self):
        self.context_lower = self.context_lower.parent 

    def get_type(self, type_name):
        for i in self.types:
            if i.name == type_name:
                return i
        return None
    
    def get_type_for(self, symbol):
        pass
    def defineSymbol(self, symbol, type) -> bool:
        return False
    
    def create_type(self, name, args = []):
        if (self.get_type(name) != None):
            return False
        self.types.append(Type(name, args))
        return True

class NodeClass:
    def __init__(self, name, sons = [], parent = None) -> None:
        self.name = name
        self.sons = sons
        self.parent = parent

class Hierarchy:
    def __init__(self) -> None:
        self.root = NodeClass("object", [NodeClass("number"), NodeClass("string"), NodeClass("boolean"), 
                                         NodeClass("Iterable", [NodeClass("Vector")])])

    def get_type(self, actual: NodeClass, name):
        if actual == None:
            return None
        if (actual.name == name):
            return actual
        for i in actual.sons:
            g = self.get_type(i, name) 
            if g != None:
                return g
        return None
    
    def is_type(self, name):
        return True if self.get_type(self.root, name) != None else False
    
    def add_type(self, name, ancestor_name):
        check_name = self.get_type(self.root, name)
        if check_name != None:
            return None
        ancestor = self.get_type(self.root, ancestor_name)
        if ancestor != None:
            ancestor.sons.append(NodeClass(name, [], ancestor))
    
    def get_ancestors(self, actual: NodeClass, name):
        if (actual.name == name):
            return [actual]
        for i in actual.sons:
            v = self.get_ancestors(i, name)
            if len(v) > 0:
                return v + [actual]
        return []

    def get_lca(self, nodo1, nodo2):
        t1 = self.get_ancestors(self.root, nodo1)
        t2 = self.get_ancestors(self.root, nodo2)
        path = {}
        for i in t1:
            path[i.name] = True
        for i in t2:
            if path.get(i.name):
                return i
        return self.root
    
# construye el contexto de los tipos definidos y chequea que no hayan dos con el mismo nombre
class TypeCollectorVisitor(Visitor):
    def __init__(self, context : Context):
        self.context = context
        self.error_logger = ErrorLogger()
    
    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            i.accept(self)
    
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass

    def visit_method_node(self, method_node : MethodNode):
        pass

    def visit_type_node(self, type_node : TypeNode):
        if self.context.create_type(type_node.id.lexeme, []) == False:
            self.error_logger.add("variable ya creada")
            return

    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        if self.context.create_type(protocol_node.id.lexeme, None) == False:
            self.error_logger.add("variable ya creada")

    def visit_let_node(self, let_node : LetNode):
        pass

    def visit_while_node(self, while_node : WhileNode):
        pass

    def visit_if_node(self, if_node : IfNode):
        pass

    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    def visit_destructor_node(self, destructor_node : DestructorNode):
        pass

    def visit_block_node(self, block_node : BlockNode):
        pass

    def visit_call_node(self, call_node : CallNode):
        pass

    def visit_get_node(self, get_node : GetNode):
        pass

    def visit_set_node(self, set_node : SetNode):
        pass

    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        pass

    def visit_new_node(self, new_node : NewNode):
        pass

    def visit_binary_node(self, binary_node : BinaryNode):
        pass
    def visit_unary_node(self, binary_node : UnaryNode):
        
        return True

    def visit_literal_node(self, literal_node : LiteralNode):
        pass
 

class TypeBuilderVisitor(Visitor):
    def __init__(self, context : Context, hierarchy : Hierarchy):
        self.context = context
        self.actual_type = None
        self.hierarchy = hierarchy
        self.error_logger = ErrorLogger()

    def visit_program_node(self, program_node : ProgramNode):
        j = 1
        for i in program_node.decls:
            if j < len(program_node.decls):
                i.accept(self)
            j+=1
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        if self.actual_type != None:
            if attribute_node.id.lexeme == "self":
                self.error_logger.add("no se puede usar el self como atributo a definir")
            if self.actual_type.get_attribute(attribute_node.id.lexeme) == None:
                self.actual_type.define_attribute(attribute_node.id.lexeme, attribute_node.type.lexeme if attribute_node.type != None else "object")
                return    
            self.error_logger.add("atributo ya definido " + attribute_node.id.lexeme + " de " + self.actual_type.name)

    def visit_method_node(self, method_node : MethodNode):
        if self.actual_type != None:
            if self.actual_type.get_method(method_node.id.lexeme, method_node.params) == None:
            
                return_type = method_node.type.lexeme if method_node.type != None else None
                    # revisa que existe el tipo de retorno 
                if return_type != None and self.hierarchy.is_type(return_type):
                    dict = {}
                    # que los parametros no se definan dos veces el mismo nombre
                    # que no tengan tipos incorrectos
                    for (i, j) in method_node.params :
                        if dict.get(i.lexeme) == None:
                            param_type = j.lexeme if j != None else None
                            
                            if param_type != None and self.hierarchy.is_type(param_type):
                                dict[i.lexeme] = param_type
                            else:
                                self.error_logger.add("tipo de parametro incorrecto")
                        else:
                            self.error_logger.add("parametro ya existe metodo " + method_node.id.lexeme +  " - " + i.lexeme)
                    self.actual_type.define_method(method_node.id.lexeme, method_node.type.lexeme if method_node.type != None else "object", method_node.params)
                else:
                    self.error_logger.add("tipo de retorno incorrecto metodo en build")
                return
            self.error_logger.add("metodo ya definido " + method_node.id.lexeme + " de " + self.actual_type.name)
            
    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(type_node.id.lexeme)
        if type_node.ancestor_id != None:
            ancestor_type = self.context.get_type(type_node.ancestor_id.lexeme)
            if ancestor_type == False:
                self.error_logger.add("clase herada incorrectamente")
            else: 
                self.hierarchy.add_type(type_node.id.lexeme, type_node.ancestor_id.lexeme)
        else:
            self.hierarchy.add_type(type_node.id.lexeme, "object")
        for i in type_node.methods:
            if i.id.lexeme == "build":
                args = []
                dict = {}
                    # que los parametros no se definan dos veces el mismo nombre
                    # que no tengan tipos incorrectos
                for m in i.params:
                    (j, k) = m 
                    args.append((j.lexeme, k.lexeme if k != None else None))
                
                for i in type_node.methods:
                    if i.id.lexeme == "build": 
                        for j in i.body.exprs:
                            j.accept(self)

                if self.actual_type:
                    self.actual_type.add_args(args)
            else:
                i.accept(self)
        self.actual_type = last_type

    def visit_signature_node(self, signature_node : SignatureNode):
        if self.actual_type != None:
            if self.actual_type.get_method(signature_node.id.lexeme, len(signature_node.params)) == None:
                self.actual_type.define_method(signature_node.id.lexeme, signature_node.type.lexeme if signature_node.type != None else "object", signature_node.params)
                return_type = signature_node.type.lexeme if signature_node.type != None else None
                # revisa que existe el tipo de retorno 
                if return_type != None and self.hierarchy.is_type(return_type):
                    dict = {}
                    # que los parametros no se definan dos veces el mismo nombre
                    # que no tengan tipos incorrectos
                    for (i, j) in signature_node.params :
                        if dict.get(i.lexeme) == None:
                            param_type = j.lexeme if j != None else None
                            if param_type != None and self.hierarchy.is_type(param_type):
                                dict[i.lexeme] = param_type
                            else:
                                self.error_logger.add("tipo de parametro incorrecto de signature " + signature_node.id.lexeme)
                        else:
                            self.error_logger.add("parametro ya existe de signature " + signature_node.id.lexeme)
                    self.actual_type.define_method(signature_node.id.lexeme, signature_node.type.lexeme if signature_node.type != None else "object", signature_node.params)
                else:
                    self.error_logger.add("tipo de retorno incorrecto de signature " + signature_node.id.lexeme)
                return
                
            self.error_logger.add("metodo ya definido " + signature_node.id.lexeme + " de " + self.actual_type.name)

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(protocol_node.id.lexeme)
        if protocol_node.ancestor_node != None:
            ancestor_type = self.context.get_type(protocol_node.ancestor_node.lexeme)
            if ancestor_type == False:
                self.error_logger.add("clase herada incorrectamente")
            if ancestor_type.args != None:
                self.error_logger.add("no se puede heredar un protocolo de un tipo")
            self.hierarchy.add_type(protocol_node.id.lexeme, protocol_node.ancestor_node.lexeme)
        else:
            self.hierarchy.add_type(protocol_node.id.lexeme, "object")
        for i in protocol_node.signatures:
            i.accept(self)
            
        self.actual_type = last_type

    def visit_let_node(self, let_node : LetNode):
        pass

    def visit_while_node(self, while_node : WhileNode):
        pass

    def visit_if_node(self, if_node : IfNode):
        pass

    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    def visit_destructor_node(self, destructor_node : DestructorNode):
        pass

    def visit_block_node(self, block_node : BlockNode):
        for i in block_node.exprs:
            i.accept(self)

    def visit_call_node(self, call_node : CallNode):
        pass

    def visit_get_node(self, get_node : GetNode):
        pass

    def visit_set_node(self, set_node : SetNode):
        pass

    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        pass

    def visit_new_node(self, new_node : NewNode):
        pass

    def visit_binary_node(self, binary_node : BinaryNode):
        pass

    def visit_literal_node(self, literal_node : LiteralNode):
        pass
    def visit_unary_node(self, binary_node : UnaryNode):
        
        return True


class TypeFunctionVisitor(Visitor):
    def __init__(self, context : Context, hierarchy : Hierarchy):
        self.context = context
        self.actual_type = None
        self.hierarchy = hierarchy
        self.error_logger = ErrorLogger()

    def visit_program_node(self, program_node : ProgramNode):
        j = 1
        for i in program_node.decls:
            if j < len(program_node.decls):
                i.accept(self)
            j+=1

    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass
    def visit_method_node(self, method_node : MethodNode):
        id = method_node.id.lexeme
        args = method_node.params
        ret = method_node.type.lexeme if method_node.type != None else "object"

        if (self.context.is_defined_func(id, args)) == None:
            return_type = method_node.type.lexeme if method_node.type != None else None
            # revisa que existe el tipo de retorno 
            if return_type != None and self.hierarchy.is_type(return_type):
                dict = {}
                # que los parametros no se definan dos veces el mismo nombre
                # que no tengan tipos incorrectos
                params = []
                for (i, j) in method_node.params:
                    if dict.get(i.lexeme) == None:
                        param_type = j.lexeme if j != None else None
                        if param_type != None and self.hierarchy.is_type(param_type):
                            dict[i.lexeme] = param_type
                            params.append((i.lexeme, param_type))
                        else:
                            self.error_logger.add("tipo de parametro incorrecto de function " + method_node.id.lexeme)
                    else:
                        self.error_logger.add("parametro ya existe de function " + method_node.id.lexeme)
            
                self.context.define_func(id, ret, args)
                #revisamos el cuerpo de la funcion
                self.context.create_child_context()
                for i in params:
                    self.context.define(i[0], i[1])
                # method_node.body.accept(self)
                self.context.remove_child_context()
            else:
                self.error_logger.add("tipo de retorno incorrecto de function " + method_node.id.lexeme)
            return
            
        self.error_logger.add("function ya definido " + method_node.id.lexeme )

    def visit_type_node(self, type_node : TypeNode):
        pass
    def visit_signature_node(self, signature_node : SignatureNode):
        pass
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass
    def visit_let_node(self, let_node : LetNode):
        pass
    def visit_while_node(self, while_node : WhileNode):
        pass
    def visit_for_node(self, for_node : ForNode):
        pass
    def visit_if_node(self, if_node : IfNode):
        pass
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass
    def visit_destructor_node(self, destructor_node : DestructorNode):
        pass
    def visit_block_node(self, block_node : BlockNode):
        pass
    def visit_call_node(self, call_node : CallNode):
        pass
    def visit_get_node(self, get_node : GetNode):
        pass
    def visit_set_node(self, set_node : SetNode):
        pass
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        pass
    def visit_new_node(self, new_node : NewNode):
        pass
    def visit_binary_node(self, binary_node : BinaryNode):
        pass
    def visit_unary_node(self, unary_node : UnaryNode):
        pass
    def visit_literal_node(self, literal_node : LiteralNode):
        pass



class TypeCheckerVisitor(Visitor):
    def __init__(self, context : Context, hierarchy : Hierarchy):
        self.context = context
        self.actual_type = None
        self.hierarchy = hierarchy
        self.error_logger = ErrorLogger()
        self.queue_call = []
        self.is_call_node = False # pq no se si un call node deriva en literal como tratar el literal como variable o como metodo
        self.is_use_self = False # self.Ladrar(1).Ladrar en este caso hace falta saber que ya se uso el self
        self.analize_attr_type = False # para las variables que declare como atributo de un tipo tenga de nombre self.id

    def get_type_all_function(self, type_name, func_name, args):
        type = self.context.get_type(type)
        ancestors = self.hierarchy.get_ancestors(self.hierarchy.root, type_name)
        methods = []
        for i in ancestors:
            a = self.context.get_type(i.name)
            print(a.name)
        return []

    def visit_program_node(self, program_node : ProgramNode):
        value = ""
        for i in program_node.decls:
            value = i.accept(self)

    def visit_attribute_node(self, attribute_node : AttributeNode):
        id = attribute_node.id.lexeme
        if self.actual_type != None and self.analize_attr_type == True: 
            id = 'self.' + id
        if self.context.is_defined_local(id) == False: # variable no declarada antes
            body = attribute_node.body.accept(self)
            if (attribute_node.type != None): # si viene con tipo
                if (attribute_node.type.lexeme == body): # si coinciden los tipos
                    self.context.define(id, body.type, body.value)
                    return 
                self.error_logger.add("atributo " + id + " con tipo incorrecto")
                return
            self.context.define(id, body.type, body.value)
            return
        self.error_logger.add("atributo " + id + " ya definido")
        
    def visit_method_node(self, method_node : MethodNode):
        ret = method_node.body.accept(self)
        id = method_node.id.lexeme
        if id == "main":
            return ret
        if ret != None:
            type_func = None
            if self.actual_type == None:
                type_func = self.context.is_defined_func(id, [])
            else:
                type_func = self.actual_type.get_method(id, [])
            if type_func != None:
                if (self.hierarchy.get_lca(ret.type, type_func.type).name) == type_func.type:
                    return ret
        self.error_logger.add("metodo no cumple " + id + " retorno con el tipo establecido")
        return ComputedValue(None, None)

    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(type_node.id.lexeme) 
        self.context.create_child_context()
        self.context.define("self", self.actual_type.name, "self")
        self.context.define_func("base", "base", []) # base es un llamado de funcion

        # necesita revisar que el tipo implementa todos los metodos de su protocolo
        ancient = self.hierarchy.get_type(self.hierarchy.root, self.actual_type.name).parent
        if (ancient != None and ancient.name != "object"):
            methods_ancient = self.context.get_type(ancient.name).method 
            for i in methods_ancient:
                mk = False
                for j in self.actual_type.method:
                    if j.name != i.name and j.type != i.type and j.args != i.args:
                        mk = True
                if mk == False:
                    self.error_logger.add("metodo " + i.name + " no implementado")

        for i in self.actual_type.method:
            self.context.context_lower.method.append(Method("self." + i.name, i.type, i.args))
        for i in type_node.methods:
            if i.id.lexeme == "build":
                args = []
                for j in i.params:
                    self.context.define(j[0].lexeme, j[1].lexeme if j[1] != None else None)
                for j in i.body.exprs:
                    self.analize_attr_type = True
                    j.accept(self)
                    self.analize_attr_type = False
                for j in i.params:
                    self.context.remove_define(j[0].lexeme)
            else:
                i.accept(self)
        self.context.remove_child_context()
        self.actual_type = last_type

    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass

    def visit_let_node(self, let_node : LetNode):
        self.context.create_child_context()
        for i in let_node.assignments:
            i.accept(self)
        value = let_node.body.accept(self)             
        self.context.remove_child_context()
        return value
    
    def visit_while_node(self, while_node : WhileNode):
        self.context.create_child_context()
        if  while_node.condition.accept(self):
            self.error_logger.add("condicion while")
        value = while_node.body.accept(self)   
        self.context.remove_child_context()
        return value


    def visit_if_node(self, if_node : IfNode):
        types = []
        for (i, j) in if_node.body:
            self.context.create_child_context()
            if i.accept(self).type != "boolean":
                self.error_logger.add("condicion mal")
                continue
            t = j.accept(self)
            types.append(t)
            self.context.remove_child_context()

        self.context.create_child_context()
        types.append(if_node.elsebody.accept(self))
        value = types[0]
        for i in range(len(types) ):
            ele = types[i]
            value = self.hierarchy.get_lca(ele, value)
        self.context.remove_child_context()
        return ComputedValue(value.name, None)

    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode): # el tipo sera vector y el valor el tipo que devolveria por defecto caualquier indice
        values = []
        types = []
        if len(explicit_vector_node.items) > 0:
            type = explicit_vector_node.items[0].accept(self).type
            for i in explicit_vector_node.items:
                j = i.accept(self)
                values.append(j.value)
                types.append(j.type)
                type = self.hierarchy.get_lca(type, j.type).name
        return ComputedValue("Vector", type)
    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        self.context.create_child_context()
        self.context.define(implicit_vector_node.target)
        if implicit_vector_node.iterable.accept(self).type != "Iterable":
            self.error_logger.add("no iterable")
            return ComputedValue('object')
        value = implicit_vector_node.result.accept(self)
        self.context.remove_child_context()
        return value

    def visit_destructor_node(self, destructor_node : DestructorNode):
        new = destructor_node.expr.accept(self)
        id = destructor_node.id.lexeme
        if self.actual_type != None and id == "self" and self.context.get("self").value == "self" and self.context.get("self").type == self.actual_type.name:
            self.error_logger.add("no se puede usar el self de un tipo en el destructor")
            return ComputedValue(None, None)
        if self.context.is_defined(id.lexeme) == True:
            type = self.context.get(id.lexeme).type
            self.context.set(id.lexeme, new.type)
            return ComputedValue(self.hierarchy.get_lca(type, new.type).name, new.value)
        self.error_logger.add("la variable no esta definida")
        return ComputedValue(None, None)
        
    def visit_block_node(self, block_node : BlockNode):
        self.context.create_child_context()
        value = ComputedValue(None, None)
        for i in block_node.exprs:
           value = i.accept(self)
        self.context.remove_child_context()
        return value

    def visit_call_node(self, call_node : CallNode):
        self.queue_call.append("call")
        args = []
        for i in call_node.args:
            args.append(i.accept(self).type)

        if (isinstance(call_node.callee, LiteralNode)):
            self.is_call_node = True
            callee = call_node.callee.accept(self)
            self.is_call_node = False
            method = self.context.is_defined_func(callee.value, args)
            if self.context.is_defined_func(callee.value, args) != None:
                j = -1
                for i in method.args:
                    arg_type = i.type
                    j += 1
                    if j < len(args) and self.hierarchy.get_lca(args[j],arg_type).name != arg_type:
                        self.error_logger.add("argumentos incorrecto de tipo " + args[j] + " " + method.name)
                        continue
                    if j >= len(args):
                        self.error_logger.add("argumentos de mas " +  method.name)
                        continue
                if j < len(args) - 1:
                    self.error_logger.add("argumentos de menos " +  method.name)
                    self.queue_call.pop()
                    return ComputedValue(None, None)
                self.queue_call.pop()
                return ComputedValue(method.type, None)
            else:
                self.error_logger.add("intento de usar funcion no definida")
                self.queue_call.pop()
                return ComputedValue(None, None)
            
        if (isinstance(call_node.callee, GetNode)):
            self.is_call_node = True
            callee = call_node.callee.accept(self)
            self.is_call_node = False
            self.is_use_self = False
            type = self.context.get_type(callee.type)
            if type == None:
                self.error_logger.add("tipo de llamada no exite")
                self.queue_call.pop()
                return ComputedValue(None, None)
            type_method = type.get_method(callee.value, args)
            if type_method != None:
                self.queue_call.pop()
                return ComputedValue(type_method.type, None)
        self.error_logger.add("funcion no definida")
        self.queue_call.pop()
        return ComputedValue(None, None)

    def visit_get_node(self, get_node : GetNode):
        self.queue_call.append("get")
        left = get_node.left.accept(self)
        type = self.context.get_type(left.type)
        id = get_node.id.lexeme
        if self.actual_type == None:
            if type == None: 
                self.error_logger.add("tipo  no existe")
                self.queue_call.pop()
                return ComputedValue(None, None)
            if len(self.queue_call) > 1 and self.queue_call[len(self.queue_call) - 2] == "call":
                if type.get_method_whithout_params(id) != None:
                    self.queue_call.pop()
                    return ComputedValue(type.name, id)
                else:
                    self.error_logger.add("intentando acceder a un atributo privado " + id)
                    self.queue_call.pop()
                    return ComputedValue(None, None)
            else:
                self.error_logger.add("intentando acceder a un atributo privado " + id)
                self.queue_call.pop()
                return ComputedValue(None, None)
        else:
            if left.type == self.actual_type.name and left.value == "self":
                self.queue_call.append(id)
                if self.is_call_node == False:
                    attr = self.context.get(left.value +"." + id)
                    if attr != None:
                        self.queue_call.pop()
                        return ComputedValue(attr.type, None)
                    self.error_logger.add("tipo self no existe en la clase")
                    self.queue_call.pop()
                    return ComputedValue(None, None)
                else:
                    methods = self.context.is_defined_func_whithout_params(left.value +"." + id)
                    if methods != None:
                        self.queue_call.pop()
                        return ComputedValue(self.actual_type.name, id)
                    self.error_logger.add("tipo self no existe en la clase")
            else:
                if type == None: 
                    self.error_logger.add("tipo  no existe")
                    self.queue_call.pop()
                    return ComputedValue(None, None)
                if type.get_method_whithout_params(id) != None:
                    self.queue_call.pop()
                    return ComputedValue(type.name, id)
                else:
                    self.error_logger.add("intentando acceder a un atributo privado " + id)
                    self.queue_call.pop()
                    return ComputedValue(None, None)
        self.error_logger.add("get node fallo")
        self.queue_call.pop()
        return ComputedValue(None, None)

    def visit_set_node(self, set_node : SetNode):
        left = set_node.left.accept(self)
        type = self.context.get_type(left.type)
        if self.actual_type == None:
            if type == None:
                self.error_logger.add("tipo  no existe")
                return ComputedValue(None, None)
            
            self.error_logger.add("intentando acceder a un atributo privado")
            return ComputedValue(None, None)
        else:
            if left.value == "self":
                attr = self.context.get(left.value +"." + set_node.id.lexeme)
                if attr != None:
                    return ComputedValue(attr.type, None)
                self.error_logger.add("tipo self no existe en la clase") 
                return ComputedValue(None, None)
        return ComputedValue(None, None)

    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        left = vector_set_node.left.accept(self)
        if left.type == "Vector":
            vector_set_node.index
            vector_set_node.value
        else:
            self.error_logger.add("no valido vector")
            return ComputedValue(None, None)

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        left = vector_get_node.left.accept(self)
        index = vector_get_node.index.accept(self)
        if (isinstance(left.type, Vector) and index.type == "number"):
            if index.value == None:
                value = left.type.values[0]
                for i in range(len(left.type.values)):
                    ele = left.type.values[i]
                    value = self.hierarchy.get_lca(ele, value)
                return ComputedValue(value, None)
            if index.value >= len(left.value):
                self.error_logger.add("indice fuera de rango")
                return ComputedValue("object")
            return left.value[index.value]

    def visit_new_node(self, new_node : NewNode):
        type = self.context.get_type(new_node.id.lexeme) 
        if type != None:
            args = type.args
            mk = 0
            for (i, j) in enumerate(new_node.args, 0):
                arg_type = j.accept(self)
                mk = i 
                if i < len(args) and args[i].type != arg_type.type:
                    self.error_logger.add("argumentos incorrecto de tipo " + args[i].type + " " + new_node.id.lexeme)
                    continue
                if i >= len(args):
                    self.error_logger.add("argumentos de mas " + new_node.id.lexeme)
                    continue
            if i < len(args) - 1:
                self.error_logger.add("argumentos de menos " + new_node.id.lexeme)
            return ComputedValue(type.name)
        self.error_logger.add("clase no definida " + new_node.id.lexeme)
        return ComputedValue("object")

    def visit_binary_node(self, binary_node : BinaryNode):
        type = None
        value = None
        msg = "" 
        match binary_node.op.lexeme:
            case "==":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "boolean"
                if left.type == right.type:
                    value = None
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        if left.value == right.value:
                            value = True
                        else:
                            value = False
                else:
                    value = False

            case ">=":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "boolean"
                if left.type == right.type:
                    value = None
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        if left.value >= right.value:
                            value = True
                        else:
                            value = False
                else:
                    value = False
            
            case "<=":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "boolean"
                if left.type == right.type:
                    value = None
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        if left.value <= right.value:
                            value = True
                        else:
                            value = False
                else:
                    value = False

            case "<":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "boolean"
                if left.type == right.type:
                    value = None
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        if left.value < right.value:
                            value = True
                        else:
                            value = False
                else:
                    value = False

            case ">":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "boolean"
                if left.type == right.type:
                    value = None
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        if left.value > right.value:
                            value = True
                        else:
                            value = False
                else:
                    value = False
            
            case "+":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "number" and right.type == "number":
                    type = "number"
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        value = left.value + right.value
                else:
                    msg = "error tipos en suma"
                    value = None
                    type = None
                
            case "-":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "number" and right.type == "number":
                    type = "number"
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        value = left.value - right.value
                else:
                    msg = "error tipos en -"
                    value = None
                    type = None
            
            case "*":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "number" and right.type == "number":
                    type = "number"
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        value = left.value * right.value
                else:
                    msg = "error tipos en *"
                    value = None
                    type = None
            
            case "/":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "number" and right.type == "number":
                    type = "number"
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        if (right.value == 0):
                            msg = "division por cero"
                            type = None
                            value = None
                        else:
                            value = left.value / right.value
                else:
                    msg = "error tipos en /"
                    value = None
                    type = None
            
            case "is":
                left = binary_node.left.accept(self)
                if isinstance(binary_node.right, LiteralNode) == False:
                    self.error_logger.add("no viene un tipo en el is")
                    return ComputedValue(None, None)
                self.queue_call.append("is")
                right = binary_node.right.accept(self)
                self.queue_call.pop()

                if (self.hierarchy.is_type(right.type)) == None:
                    self.error_logger.add("en el is no hay tipo existe")
                    return ComputedValue(None, None)
                return ComputedValue("boolean", None)

            case "as":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                left = binary_node.left.accept(self)
                if isinstance(binary_node.right, LiteralNode) == False:
                    self.error_logger.add("no viene un tipo en el as")
                    return ComputedValue(None, None)
                self.queue_call.append("as")
                right = binary_node.right.accept(self)
                self.queue_call.pop()

                if self.hierarchy.get_lca(left.type, right.type).name == right.type:
                    self.error_logger.add("en el as no hay tipo existe")
                    return ComputedValue(None, None)
                return ComputedValue(left.type == right.type)
            case "@":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)

            case "@@":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)

        value = ComputedValue(type, value)
        if msg != "":
            self.error_logger.add("inconsistencia de tipos en op binaria")
        return value
    
    def visit_unary_node(self, unary_node : UnaryNode):
        expr = unary_node.expr.accept(self)
        value = None 
        type = None
        match unary_node.op.lexeme:
            case "!":
                if expr.type != "boolean":
                    self.error_logger.add("no unaria not")
                else:
                    type = "boolean"
                    if expr.value != None:
                        value = True if expr.value == False else False
            case "+":
                if expr.type != "number":
                    self.error_logger.add("no unaria not")
                else:
                    type = "number"
                    if expr.value != None:
                        value = expr.value
            case "-":
                if expr.type != "number":
                    self.error_logger.add("no unaria not")
                else:
                    type = "number"
                    if expr.value != None:
                        value = expr.value * -1
        return ComputedValue(type, value)

    def visit_literal_node(self, literal_node : LiteralNode):
        id = literal_node.id.lexeme
        match literal_node.id.type:
            case "false":
                return ComputedValue("bolean", id)
            case "true":
                return ComputedValue("bolean", id)
            case "number":
                return ComputedValue("number", int(id))
            case "string":
                return ComputedValue("string", id)    
            case "base":
                return ComputedValue("base", "base")
            case "id":
                if id == "self":
                    self_var = self.context.get("self")
                    if self_var != None and self_var.type != "string" and self_var.value == "self":
                        value = "self"
                        type = "self"
                        if (len(self.queue_call) == 2) and self.queue_call[0] == 'get' and self.queue_call[1] == 'get':
                            self.error_logger.add("intento de acceder a variable privada")
                            value = None
                            type = None
                        if len(self.queue_call) > 2:
                            mk = self.queue_call[0]
                            if mk == "get":
                                value = None
                                type = None
                            else:
                                for i in range(1, len(self.queue_call) - 2):
                                    ele = self.queue_call[i]
                                    if mk != ele:
                                        mk = ele
                                    else:
                                        value = None
                                        type = None
                                        break
                        return ComputedValue(self_var.type, value)
                
                if len(self.queue_call) > 0 and (self.queue_call[len(self.queue_call) - 1] == "is" or self.queue_call[len(self.queue_call) - 1] == "as"):
                    return ComputedValue(id, id)
                defined = self.context.is_defined(id)
                if defined != None and self.is_call_node == False:
                    var = self.context.get(id)
                    return ComputedValue(var.type, var.value)
                if self.context.is_defined_func_whithout_params(id) == True and self.is_call_node == True:
                    var = self.context.get(id)
                    return ComputedValue(None, id)
                
                self.error_logger.add("variable no definida " + id)
        return ComputedValue(None, None)




class SemanticAnalysis:
    def __init__(self) -> None:
        pass
    
    def run(self, ast):
        context = Context()
        hierarchy = Hierarchy()
        context.define_func("print", "object", [(Token("object", "name"), Token("object", "object"))])

        typeCollectorVisitor = TypeCollectorVisitor(context)
        ast.accept(typeCollectorVisitor)
        typeBuilderVisitor = TypeBuilderVisitor(context, hierarchy)
        ast.accept(typeBuilderVisitor)
        typeFunctionVisitor = TypeFunctionVisitor(context, hierarchy)
        ast.accept(typeFunctionVisitor)
        typeCheckerVisitor = TypeCheckerVisitor(context, hierarchy)
        ast.accept(typeCheckerVisitor)
        
        err1 = typeCollectorVisitor.error_logger
        err2 = typeBuilderVisitor.error_logger
        err3 = typeFunctionVisitor.error_logger
        err4 = typeCheckerVisitor.error_logger
        err1.log_errors()
        err2.log_errors()
        err3.log_errors()
        err4.log_errors()

 