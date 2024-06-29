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
            if i.name == name and len(i.args) == len(args):
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
    
    def is_defined_func(self, name, args) -> bool:
        for i in self.method:
            if i.name == name and len(i.args) == len(args):
                return i
        return None
    
    def get(self, name):
        return self.dict.get(name)

    def define(self, var, type, value = None) -> bool:
        if self.is_defined(var):
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
    
    def is_defined_func(self, func, args) -> bool:
        return self.context_lower.is_defined_func(func, args)

    def get(self, name):
        return self.context_lower.get(name) or self.context_lower.parent != None and self.context_lower.parent.get(name)      
    
    def get_func_whithout_params(self, name):
        return self.context_lower.dict[name]    
    
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
        print(self.context_lower.parent.dict, self.context_lower.dict.get('num'))
        self.context_lower = self.context_lower.parent 
        print(self.context_lower.parent, self.context_lower.dict)

    def get_type(self, type_name):
        for i in self.types:
            if i.name == type_name:
                return i
        return None
    
    def get_type_for(self, symbol):
        pass
    def defineSymbol(self, symbol, type) -> bool:
        return False
    
    def create_type(self, name, args):
        if (self.get_type(name) != None):
            return False
        self.types.append(Type(name, args))
        return True

class NodeClass:
    def __init__(self, name, sons = [], parent = None) -> None:
        self.name = name
        self.sons = sons
        self.parent = None
class Hierarchy:
    def __init__(self) -> None:
        self.root = NodeClass("object", [NodeClass("number"), NodeClass("string"), NodeClass("boolean"), 
                                         NodeClass("Iterable", [NodeClass("Vector")])])

    def get_type(self, actual: NodeClass, name):
        if (actual.name == name):
            return actual
        for i in actual.sons:
            if self.get_type(i, name) != None:
                return i
        return None
    
    def is_type(self, name):
        return True if self.get_type(self.root, name) != None else False
    
    def add_type(self, name, ancestor_name):
        check_name = self.get_type(self.root, name)
        if check_name != None:
            return None
        ancestor = self.get_type(self.root, ancestor_name)
        if ancestor != None:
            ancestor.sons.append(name)
    
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
                    self.error_logger.add("tipo de retorno incorrecto")
                return
            self.error_logger.add("metodo ya definido " + method_node.id.lexeme + " de " + self.actual_type.name)
            
    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(type_node.id.lexeme)
        if type_node.ancestor_id != None:
            ancestor_type = self.context.get_type(type_node.ancestor_id.lexeme)
            if ancestor_type == False:
                self.error_logger.add("clase herada incorrectamente")
            self.hierarchy.add_type(type_node.id.lexeme, type_node.ancestor_id.lexeme)
        for i in type_node.methods:
            if i.id.lexeme == "build":
                args = []
                dict = {}
                    # que los parametros no se definan dos veces el mismo nombre
                    # que no tengan tipos incorrectos
                for m in i.params:
                    (j, k) = m 
                    args.append((j.lexeme, k.lexeme if k != None else None))
                if self.actual_type:
                    self.actual_type.add_args(args)
            else:
                i.accept(self)
        self.actual_type = last_type

    def visit_signature_node(self, signature_node : SignatureNode):
        if self.actual_type != None:
            if self.actual_type.get_method(signature_node.id.lexeme, len(signature_node.params)) == None:
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
            self.hierarchy.add_type(protocol_node.id.lexeme, protocol_node.ancestor_node.lexeme)
        
        for i in protocol_node.signatures:
            i.accept(self)
            
        self.actual_type = last_type

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


    def visit_program_node(self, program_node : ProgramNode):
        value = ""
        for i in program_node.decls:
            value = i.accept(self)
        print("retorno ", value.type, value.value)

    def visit_attribute_node(self, attribute_node : AttributeNode):
        id = attribute_node.id.lexeme
        if self.actual_type != None:
            id = 'self.' + id
        if self.context.is_defined(id) == False: # variable no declarada antes
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
        return method_node.body.accept(self)

    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(type_node.id.lexeme) 
        self.context.create_child_context()
        self.context.define("self")
        for i in type_node.methods:
            if i.id.lexeme == "build":
                args = []
                for j in i.params:
                    self.context.define(j[0].lexeme, j[1].lexeme if j[1] != None else None)
                for j in i.body.exprs:
                    j.accept(self)
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

    def visit_for_node(self, for_node : ForNode):
        self.context.create_child_context()
        if for_node.iterable.accept(self) != "Iterable":
            self.error_logger.add("no iterable")
        if self.context.is_defined(for_node.target.lexeme) != None:
            self.error_logger.add("target for ya definida")
        value = for_node.body.accept(self)
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
        if self.context.is_defined(destructor_node.id.lexeme) == True:
            type = self.context.get(destructor_node.id.lexeme).type
            self.context.set(destructor_node.id.lexeme, new.type)
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
        callee = call_node.callee.accept(self)
        if (isinstance(call_node.callee, GetNode)):
            type = self.context.get_type(callee.type.name)
            args = []
            for i in call_node.args:
                args.append(i.accept(self).type)
            type_method = type.get_method(callee.value, args)
            if type_method != None:
                return ComputedValue(type_method.type, None)
        self.error_logger.add("funcion no definida")
        return ComputedValue(None, None)

    def visit_get_node(self, get_node : GetNode):
        left = get_node.left.accept(self)
        type = self.context.get_type(left.type)
        if self.actual_type == None:
            if type.get_attribute(id) == None:
                return ComputedValue(type, get_node.id.lexeme)
            else:
                self.error_logger.add("intentando acceder a un atributo privado")
                return ComputedValue(None, None)
        else:
            if left.value == "self":
                return ComputedValue(None, None)
        return ComputedValue(None, None)

    def visit_set_node(self, set_node : SetNode):
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
            mk = False
            for (i, j) in enumerate(new_node.args, 0):
                arg_type = j.accept(self)
                if i < len(args) and args[i].type != arg_type.type:
                    self.error_logger.add("argumentos incorrecto de tipo " + args[i].type + " " + new_node.id.lexeme)
                    continue
                if i >= len(args):
                    self.error_logger.add("argumentos de mas " + new_node.id.lexeme)
                    continue
                    
            return ComputedValue(type.name)
        self.error_logger.add("clase no definida " + new_node.id.lexeme)
        return ComputedValue("object")

    def visit_binary_node(self, binary_node : BinaryNode):
        left = binary_node.left.accept(self)
        right = binary_node.right.accept(self)
        type = None
        value = None
        msg = "" 
        match binary_node.op.lexeme:
            case "==":
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
            case "self":
                return ComputedValue("self", "self")
            case "base":
                return ComputedValue("base", "base")
            case "id":
                if self.context.is_defined(id):
                    var = self.context.get(id)
                    return ComputedValue(var.type, var.value)
                self.error_logger.add("variable no definida " + id)
        return ComputedValue(None, None)




class SemanticAnalysis:
    def __init__(self) -> None:
        pass
    
    def run(self, ast):
        context = Context()
        hierarchy = Hierarchy()

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
