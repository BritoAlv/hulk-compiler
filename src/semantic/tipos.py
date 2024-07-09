from asyncio import protocols
import math
from pickletools import long4
from re import L
from sqlalchemy import False_
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
    def __init__(self, name, args, methods = [], attribute = []) -> None:
        self.name = name
        self.attribute = attribute
        self.method = methods
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
        get = self.dict.get(name)
        if get != None:
            return get
        if self.parent != None:
            return self.parent.get(name)
        return None

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
    
    def set(self, name, type_new,value):
        self.context_lower.dict[name] = ComputedValue(type_new, value)

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
    
    def get_protocols(self):
        protocols = []
        for i in self.types:
            if i.args == None:
                protocols.append(i)
        return protocols

    def defineSymbol(self, symbol, type) -> bool:
        return False
    
    def create_type(self, name, args = [], methods = []):
        if (self.get_type(name) != None):
            return False
        self.types.append(Type(name, args, methods))
        return True

class NodeClass:
    def __init__(self, name, sons = [], parent = None) -> None:
        self.name = name
        self.sons = sons
        self.parent = parent

class Hierarchy:
    def __init__(self) -> None:
        self.root = NodeClass("Object", [NodeClass("Number"), NodeClass("String"), NodeClass("Boolean"), 
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
                self.actual_type.define_attribute(attribute_node.id.lexeme, attribute_node.type.lexeme if attribute_node.type != None else "Object")
                return    
            self.error_logger.add("atributo ya definido " + attribute_node.id.lexeme + " de " + self.actual_type.name)

    def visit_method_node(self, method_node : MethodNode):
        if self.actual_type != None:
            if self.actual_type.get_method(method_node.id.lexeme, method_node.params) == None:
            
                return_type = method_node.type.lexeme if method_node.type != None else None
                    # revisa que existe el tipo de retorno 
                if return_type != None and self.context.get_type(return_type) != None:
                    dict = {}
                    # que los parametros no se definan dos veces el mismo nombre
                    # que no tengan tipos incorrectos
                    for (i, j) in method_node.params :
                        if dict.get(i.lexeme) == None:
                            param_type = j.lexeme if j != None else None
                            
                            if param_type != None and self.context.get_type(param_type) != None:
                                dict[i.lexeme] = param_type
                            else:
                                dict[i.lexeme] = "Object"
                                self.error_logger.add("tipo de parametro incorrecto")
                        else:
                            self.error_logger.add("parametro ya existe metodo " + method_node.id.lexeme +  " - " + i.lexeme)
                    self.actual_type.define_method(method_node.id.lexeme, method_node.type.lexeme if method_node.type != None else "Object", method_node.params)
                else:
                    self.actual_type.define_method(method_node.id.lexeme, "Object", [])
                    self.error_logger.add("tipo de retorno incorrecto metodo en build")
                return
            self.error_logger.add("metodo ya definido " + method_node.id.lexeme + " de " + self.actual_type.name)
            
    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(type_node.id.lexeme)
        if type_node.ancestor_id != None:
            ancestor_type = self.context.get_type(type_node.ancestor_id.lexeme)
            if ancestor_type == None:
                self.hierarchy.add_type(type_node.id.lexeme, "Object")
                self.error_logger.add("clase herada incorrectamente")
            else: 
                self.hierarchy.add_type(type_node.id.lexeme, type_node.ancestor_id.lexeme)
        else:
            self.hierarchy.add_type(type_node.id.lexeme, "Object")
        for i in type_node.methods:
            if i.id.lexeme == "build":
                args = []
                dict = {}
                    # que los parametros no se definan dos veces el mismo nombre
                    # que no tengan tipos incorrectos
                for m in i.params:
                    (j, k) = m 
                    args.append((j.lexeme, k.lexeme if k != None else None))
                 
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
                self.actual_type.define_method(signature_node.id.lexeme, signature_node.type.lexeme if signature_node.type != None else "Object", signature_node.params)
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
                    self.actual_type.define_method(signature_node.id.lexeme, signature_node.type.lexeme if signature_node.type != None else "Object", signature_node.params)
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
            self.hierarchy.add_type(protocol_node.id.lexeme, "Object")
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
        ret = method_node.type.lexeme if method_node.type != None else "Object"

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
                self.context.define_func(id, "Object", args)
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
        self.is_instanciated_type_attr = False # para no poder usar un atributo en cuando inicializo los tipos
        self.analize_attr_type = False # para las variables que declare como atributo de un tipo tenga de nombre self.id

    def get_type_all_function(self, type_name):
        type = self.context.get_type(type_name)
        ancestors = self.hierarchy.get_ancestors(self.hierarchy.root, type_name)
        methods = []
        for i in ancestors:
            a = self.context.get_type(i.name)
            if a != None:
                for j in a.method:
                    methods.append(j)
        return methods
    
    def match_args(self, func_args, args):
        if len(args) < len(func_args) - 1:
            return False
        if len(args) > len(func_args):
            return False
        for i in range(len(args)):
            if func_args[i] == None:
                return False
            f = func_args[i].type
            a = args[i]
            if self.hierarchy.get_lca(f, a).name != f:
                return False 
        return True
    
    def match_args_types(self, func_args, args):
        if len(args) < len(func_args) - 1:
            return False
        if len(args) > len(func_args):
            return False
        for i in range(len(args)):
            if func_args[i] == None:
                return False
            f = func_args[i].type
            a = args[i]
            if f != a:
                return False 
        return True
    
    def get_type_function(self, type_name, func_name, args):
        methods = self.get_type_all_function(type_name)
        for i in methods:
            match = self.match_args(i.args, args)
            if i.name == func_name and match == True:
                return i
        return None
    
    def type_implemets_protocol(self, type: Type, protocol: Type):
        for i in protocol.method:
            mk = False
            type_method = self.get_type_all_function(type.name)
            for j in type_method:
                if i.name == j.name and i.type == j.type and self.match_args_types(i.args, j.args):
                    mk = True 
                    break
            if mk == False:
                return False
        return True

    def type_protocols_implemented(self, type):
        protocols = self.context.get_protocols()
        implemented = []
        for i in protocols:
            if self.implemets_protocol(type, i):
                implemented.append(i)
        return implemented

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

            body_type = self.context.get_type(body.type)
            if (attribute_node.type != None): # si viene con tipo
                attr_type = self.context.get_type(attribute_node.type.lexeme)

                if attr_type == None:
                    self.error_logger.add(f"tipo no existe attribute_node.type.lexeme en linea {attribute_node.id.lexeme}")
                    if self.is_instanciated_type_attr == True:
                            return ComputedValue("Object", id)
                    self.context.set(id, "Object")
                    return
                
                # chequeo para el caso de que se le pase null entonces se establecera como el tipo que le digas si no error
                if body.type == "null": 
                        if self.is_instanciated_type_attr == True:
                            return ComputedValue(attribute_node.type.lexeme, id)
                        self.context.set(id, attribute_node.type.lexeme)
                        return

                
                if attr_type.args == None and body_type.args != None:
                    if self.type_implemets_protocol(attr_type, body_type): # si coinciden los tipos
                        if self.is_instanciated_type_attr == True:
                            return ComputedValue(body.type, id)
                        self.context.define(id, body.type, body.value)
                        return 
                else:
                    if self.hierarchy.get_lca(attribute_node.type.lexeme, body.type): # si coinciden los tipos
                        if self.is_instanciated_type_attr == True:
                            return ComputedValue(body.type, id)
                        self.context.define(id, body.type, body.value)
                        return 
                self.context.define(id, "Object")
                self.error_logger.add("atributo " + id + " con tipo incorrecto")
                return
            else:
                    if body.type == "null": 
                        self.error_logger.add(f"al dar valor null hay que pasar un tipo a la variable")
                        if self.is_instanciated_type_attr == True:
                                return ComputedValue("Object", id)
                        self.context.set(id, "Object")
                        return
            

            if self.is_instanciated_type_attr == True:
                return ComputedValue(body.type, id)

            self.context.define(id, body.type, body.value)
            return
        else:   # pq si estoy en un let puede ya estar definida y se puede sobrescribir
            if len(self.queue_call) > 0 and (self.queue_call[len(self.queue_call) - 1]) == "let":
                body = attribute_node.body.accept(self)

                    

                body_type = self.context.get_type(body.type)
                if (attribute_node.type != None): # si viene con tipo
                    attr_type = self.context.get_type(attribute_node.type.lexeme)

                    if attr_type == None: # tipo no definido
                        self.error_logger.add(f"tipo no existe attribute_node.type.lexeme en linea {attribute_node.id.lexeme}")
                        if self.is_instanciated_type_attr == True:
                                return ComputedValue("Object", id)
                        self.context.set(id, "Object")
                        return
                    
                     # chequeo para el caso de que se le pase null entonces se establecera como el tipo que le digas si no error
                    if body.type == "null": 
                        if self.is_instanciated_type_attr == True:
                                return ComputedValue(attribute_node.type.lexeme, id)
                        self.context.set(id, attribute_node.type.lexeme)
                        return
  
                    if attr_type.args == None and body_type.args != None:
                        if self.type_implemets_protocol(attr_type, body_type): # si coinciden los tipos
                            if self.is_instanciated_type_attr == True:
                                return ComputedValue(body.type, id)
                            self.context.set(id, body.type, body.value)
                            return 
                    else:
                        if self.hierarchy.get_lca(attribute_node.type.lexeme, body.type): # si coinciden los tipos
                            if self.is_instanciated_type_attr == True:
                                return ComputedValue(body.type, id)
                            self.context.set(id, body.type, body.value)
                            return 
                    self.error_logger.add("atributo " + id + " con tipo incorrecto")
                    self.context.set(id, "Object")
                    return
                else:
                    if body.type == "null": 
                        self.error_logger.add(f"al dar valor null hay que pasar un tipo a la variable")
                        if self.is_instanciated_type_attr == True:
                                return ComputedValue("Object", id)
                        self.context.set(id, "Object")
                        return
                if self.is_instanciated_type_attr == True:
                    return ComputedValue(body.type, id)

                self.context.set(id, body.type, body.value)
                return
            else:
                self.error_logger.add("atributo " + id + " ya definido")
        
    def visit_method_node(self, method_node : MethodNode):
        id = method_node.id.lexeme
        attr = []
        if id == "main":
            return method_node.body.accept(self)

        if self.actual_type != None:
            method = self.actual_type.get_method(id, method_node.params)
            if method != None:
                attr = method.args
            else:
                return ComputedValue(None, None)
        else:
            method = self.context.is_defined_func(id, method_node.params)
            if method != None:
                attr = method.args
            else:
                return ComputedValue(None, None)

        self.context.create_child_context()
        if attr:
            for i in attr:
                self.context.define(i.name, i.type)
        ret = method_node.body.accept(self)
        self.context.remove_child_context()
        
        
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
        type = self.hierarchy.get_type(self.hierarchy.root, self.actual_type.name)
        if type != None:
            ancient = type.parent
            if (ancient != None and ancient.name != "Object"):
                methods_ancient = self.context.get_type(ancient.name).method 
                for i in methods_ancient:
                    mk = False
                    for j in self.actual_type.method:
                        if j.name != i.name and j.type != i.type and j.args != i.args:
                            mk = True
                    if mk == False:
                        self.error_logger.add("metodo " + i.name + " no implementado")
        else:
            self.error_logger.add(f"Tipo al heredar no existe en linea {self.actual_type.name}")
        for i in self.actual_type.method:
            self.context.context_lower.method.append(Method("self." + i.name, i.type, i.args))
        for i in type_node.methods:
            if i.id.lexeme == "build":
                args = []
                for j in i.params: # definir los parametros para el constructor
                    self.context.define(j[0].lexeme, j[1].lexeme if j[1] != None else None)
                self.is_instanciated_type_attr = True
                attr = []
                for j in i.body.exprs: # inicializar los atributos
                    self.analize_attr_type = True
                    attr.append(j.accept(self))
                    self.analize_attr_type = False
                self.is_instanciated_type_attr = False

                for j in attr:
                    self.context.define(j.value, j.type)

                for j in i.params:
                    self.context.remove_define(j[0].lexeme)
            else:
                i.accept(self)
        
        # revisar si los metodos del tipo si sobrescriben alguno heredera tiene que cumplir exacta la firma
        ancestors = self.hierarchy.get_ancestors(self.hierarchy.root, self.actual_type.name)
        for j in self.actual_type.method:
            
            for k in range(1, len(ancestors)):
                a = self.context.get_type(ancestors[k])
                if a != None:
                    for n in a.method:
                        if n.name == j.name :
                            if n.type != j.name and self.match_args_types(n.args, j.args) == False:
                                self.error_logger.add(f"metodo sobrecargado de la clase no cumple la firma linea ")

        self.context.remove_child_context()
        self.actual_type = last_type

    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass

    def visit_let_node(self, let_node : LetNode):
        self.context.create_child_context()
        self.queue_call.append("let")
        for i in let_node.assignments:
            i.accept(self)
        self.queue_call.pop()
        value = let_node.body.accept(self)             
        self.context.remove_child_context()
        return value
    
    def visit_while_node(self, while_node : WhileNode):
        self.context.create_child_context()
        condition = while_node.condition.accept(self)
        if condition.type != "Boolean":
            self.error_logger.add("condicion while")
        value = while_node.body.accept(self)   
        self.context.remove_child_context()
        return value

    def visit_if_node(self, if_node : IfNode):
        types = []
        for (i, j) in if_node.body:
            self.context.create_child_context()
            if i.accept(self).type != "Boolean":
                self.error_logger.add("condicion mal")
                continue
            t = j.accept(self)
            types.append(t)
            self.context.remove_child_context()

        self.context.create_child_context()
        types.append(if_node.elsebody.accept(self))
        value = types[0].type
        for i in range(len(types) ):
            ele = types[i]
            if ele != None:
                value = self.hierarchy.get_lca(ele.type, value).name
        self.context.remove_child_context()
        return ComputedValue(value, None)

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
        iterable = implicit_vector_node.iterable.accept(self)
        self.context.define(implicit_vector_node.target.lexeme, iterable.value if iterable.value != None else "Object")
        if self.type_implemets_protocol(self.context.get_type(iterable.type), self.context.get_type("Iterable")) == False:
            self.error_logger.add("no iterable")
            return ComputedValue('Object')
        value = implicit_vector_node.result.accept(self)
        self.context.remove_child_context()
        return ComputedValue("Vector", value.type)

    def visit_destructor_node(self, destructor_node : DestructorNode):
        new = destructor_node.expr.accept(self)
        id = destructor_node.id.lexeme
        if self.actual_type != None and id == "self" and self.context.get("self").value == "self" and self.context.get("self").type == self.actual_type.name:
            self.error_logger.add("no se puede usar el self de un tipo en el destructor")
            return ComputedValue("Object", None)
        if self.context.is_defined(id) == True:
            type = self.context.get(id).type
            id_type = self.context.get_type(type)
            new_type = self.context.get_type(new.type)
            if new_type == None:
                self.error_logger.add(f"no se le paso un tipo correcto al destructor en linea {destructor_node.id.line}")
                return ComputedValue(type, id)

            if id_type != None and id_type.args == None and new_type.args != None:
                if self.type_implemets_protocol(id_type, new_type): # si coinciden los tipos
                    return ComputedValue(type, id)
                else:
                    self.error_logger.add(f"intento de cambiar tipo a la variable {destructor_node.id.line}")
            else:
                if self.hierarchy.get_lca(type, new_type.name).name == type: # si coinciden los tipos
                    return ComputedValue(type, id)
                else:
                    self.error_logger.add(f"intento de cambiar tipo a la variable {destructor_node.id.line}")
                    return ComputedValue(type, id)


           
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

        if (isinstance(call_node.callee, LiteralNode)):
            self.is_call_node = True
            callee = call_node.callee.accept(self)
            self.is_call_node = False
            self.queue_call.pop()
            aux_queue = self.queue_call

            args = []
            for i in call_node.args:
                args.append(i.accept(self).type)
            self.queue_call = aux_queue
            method = self.context.is_defined_func(callee.value, args)
            if self.context.is_defined_func(callee.value, args) != None:
                j = -1
                for i in method.args:
                    arg_type = i.type
                    j += 1
                    if j < len(args) and self.hierarchy.get_lca(args[j],arg_type).name != arg_type:
                        self.error_logger.add(f"argumentos incorrecto de tipo {args[j]} en {method.name}")
                        continue
                    if j >= len(args):
                        self.error_logger.add("argumentos de mas " +  method.name)
                        continue
                if j < len(args) - 1:
                    self.error_logger.add("argumentos de menos " +  method.name)
                    return ComputedValue(None, None)
                return ComputedValue(method.type, None)
            else:
                self.error_logger.add("intento de usar funcion no definida")
                return ComputedValue(None, None)
            
        if (isinstance(call_node.callee, GetNode)):
            self.is_call_node = True
            callee = call_node.callee.accept(self)
            self.is_call_node = False
            self.is_use_self = False
            self.queue_call.pop()
            aux_queue = self.queue_call
            args = []
            for i in call_node.args:    
                self.queue_call = []
                # self.queue_call.append("call arg")

                args.append(i.accept(self).type)
                # self.queue_call.pop()
            self.queue_call = aux_queue
            type = self.context.get_type(callee.type)
            if type == None:
                self.error_logger.add("tipo de llamada no exite")
                return ComputedValue(None, None)
            # type_method = type.get_method(callee.value, args)
            type_method = self.get_type_function(callee.type, callee.value, args)
            if type_method != None:
                return ComputedValue(type_method.type, None)
        self.error_logger.add("funcion no definida")
        return ComputedValue(None, None)

    def visit_get_node(self, get_node : GetNode):
        self.queue_call.append("get")
        left = get_node.left.accept(self)
        type = self.context.get_type(left.type)
        id = get_node.id.lexeme
        self.queue_call.pop()
        if self.actual_type == None:
            if type == None: 
                self.error_logger.add("tipo  no existe")
                return ComputedValue(None, None)
            if len(self.queue_call) > 0 and self.queue_call[len(self.queue_call) - 1] == "call":
                if type.get_method_whithout_params(id) != None:
                    return ComputedValue(type.name, id)
                else:
                    self.error_logger.add("intentando acceder a un atributo privado " + id)
                    return ComputedValue(None, None)
            else:
                self.error_logger.add("intentando acceder a un atributo privado " + id)
                return ComputedValue(None, None)
        else:
            if left.type == self.actual_type.name and left.value == "self":
                if len(self.queue_call) == 0 or len(self.queue_call) > 0 and self.queue_call[len(self.queue_call) - 1] == "get":
                    attr = self.context.get(left.value +"." + id)
                    if attr != None:
                        return ComputedValue(attr.type, None)
                    self.error_logger.add("tipo self no existe en la clase")
                    return ComputedValue(None, None)
                else:
                    if len(self.queue_call) > 0 and self.queue_call[len(self.queue_call) - 1] == "call":

                        methods = self.context.is_defined_func_whithout_params(left.value +"." + id)
                        if methods != False:
                            return ComputedValue(self.actual_type.name, id)
                        self.error_logger.add("tipo self no existe en la clase")
            else:
                if type == None: 
                    self.error_logger.add("tipo  no existe")
                    return ComputedValue(None, None)
                if type.get_method_whithout_params(id) != None:
                    return ComputedValue(type.name, id)
                else:
                    self.error_logger.add("intentando acceder a un atributo privado " + id)
                    return ComputedValue(None, None)
        self.error_logger.add("get node fallo")
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
            if left.type == self.actual_type.name and left.value == "self":
                left_value = self.context.get(left.value +"." + set_node.id.lexeme)
                id_type = self.context.get_type(left_value.type)
                value = set_node.value.accept(self).type
                new_type = self.context.get_type(value)
                
                # revisar que el nuevo tipo cumple la firma
                if id_type != None and id_type.args == None and new_type.args != None:
                    if self.type_implemets_protocol(id_type, new_type): # si coinciden los tipos
                        if self.is_instanciated_type_attr == True:
                            return ComputedValue(type, id)
                        return 
                    else:
                        self.error_logger.add(f"intento de cambiar tipo a la variable {set_node.id.line}")
                else:
                    if new_type != None and self.hierarchy.get_lca(id_type.name, new_type.name).name == id_type.name: # si coinciden los tipos
                        return ComputedValue(type.name, None)
                    else:
                        self.error_logger.add(f"intento de cambiar tipo a la variable {set_node.id.line}")
                self.error_logger.add("tipo self no existe en la clase") 
                return ComputedValue("Object", None)
        return ComputedValue("Object", None)

    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        left = vector_set_node.left.accept(self)
        if left.type == "Vector":
            if vector_set_node.index.accept(self).type != "Number":
                self.error_logger.add(f"intento de acceder a una posicion sin pasarle un numero")
            vector_set_node.value
            id_type = self.context.get_type(left.value)
            value = vector_set_node.value.accept(self).type
            new_type = self.context.get_type(value)
            if value == "null":
                return ComputedValue(left.value, None)
                
            # revisar que el nuevo tipo cumple la firma
            if id_type != None and id_type.args == None and new_type.args != None:
                if self.type_implemets_protocol(id_type, new_type): # si coinciden los tipos
                    if self.is_instanciated_type_attr == True:
                        return ComputedValue(type, id)
                    return 
                else:
                    self.error_logger.add(f"intento de cambiar tipo a la variable ")
            else:
                if self.hierarchy.get_lca(left.value, new_type.name).name == left.value: # si coinciden los tipos
                    return ComputedValue(left.value, None)
                else:
                    self.error_logger.add(f"intento de cambiar tipo a la variable ")
        else:
            self.error_logger.add("no valido vector")
            return ComputedValue(None, None)

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        left = vector_get_node.left.accept(self)
        index = vector_get_node.index.accept(self)
        if left.type == "Vector" and index.type == "Number":
            if index.value == None:
                value = left.type.values[0]
                for i in range(len(left.type.values)):
                    ele = left.type.values[i]
                    value = self.hierarchy.get_lca(ele, value)
                return ComputedValue(value, None)
            if left.value != None and index.value >= len(left.value):
                self.error_logger.add("indice fuera de rango")
                return ComputedValue("Object")
            return ComputedValue(left.value)
        self.error_logger.add(f"forma incorrecta de obtener un vector")
        return ComputedValue("Object")
    def visit_new_node(self, new_node : NewNode):
        mk = False
        match new_node.id.lexeme:
            case "Object":
                mk = True
            case "String":
                mk = True
            case "Boolean":
                mk = True
            case "Number":
                mk = True
        if mk == True:
            self.error_logger.add(f"no se puede instanciar un tipo primitivo {new_node.id.line}")
        type = self.context.get_type(new_node.id.lexeme) 
        if type != None:
            args = type.args
            if (args == None):
                self.error_logger(f"no se puede instanciar un protocolo {new_node.id.line}")
            mk = 0
            for (i, j) in enumerate(new_node.args, 0):
                arg_type = j.accept(self)
                mk = i 
                if i < len(args) and arg_type.type == "null": # si viene null omitelo 
                    continue
                if i < len(args) and self.hierarchy.get_lca(args[i].type, arg_type.type).name != args[i].type:
                    self.error_logger.add(f"argumentos incorrecto de tipo {args[i].type} {new_node.id.lexeme}")
                    continue
                if i >= len(args):
                    self.error_logger.add("argumentos de mas " + new_node.id.lexeme)
                    continue
            if mk < len(args) - 1:
                self.error_logger.add("argumentos de menos " + new_node.id.lexeme)
            return ComputedValue(type.name)
        self.error_logger.add("clase no definida " + new_node.id.lexeme)
        return ComputedValue("Object")

    def visit_binary_node(self, binary_node : BinaryNode):
        type = None
        value = None
        msg = "" 
        op = binary_node.op.lexeme
        match op:
            case "&":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "Boolean" and left.type == right.type:
                    type = "Boolean"

            case "|":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "Boolean" and left.type == right.type:
                    type = "Boolean"

            case "==":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "Boolean"
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
                type = "Boolean"
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
                type = "Boolean"
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
                type = "Boolean"
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
                type = "Boolean"
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
                if left.type == "Number" and right.type == "Number":
                    type = "Number"
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
                if left.type == "Number" and right.type == "Number":
                    type = "Number"
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
                if left.type == "Number" and right.type == "Number":
                    type = "Number"
                    if left.value == None or right.value == None:
                        value = None
                    else:
                        value = left.value * right.value
                else:
                    msg = "error tipos en *"
                    value = None
                    type = None
            
            case "^":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                type = "Number"
                if left.type == "Number" and right.type == "Number":
                    type = "Number"
                else:
                    msg = f"error tipos en ^ en linea {binary_node.op.line}"
                    value = None
                    
            case "/":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type == "Number" and right.type == "Number":
                    type = "Number"
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

                if (self.hierarchy.is_type(right.type)) == None:
                    self.error_logger.add("en el is no hay tipo existe")
                    return ComputedValue(None, None)
                return ComputedValue("Boolean", None)

            case "as":
                left = binary_node.left.accept(self)
                if isinstance(binary_node.right, LiteralNode) == False:
                    self.error_logger.add("no viene un tipo en el as")
                    return ComputedValue(None, None)
                self.queue_call.append("as")
                right = binary_node.right.accept(self)
                self.queue_call.pop()

                type_right = self.context.get_type(right.type)
                if type_right != None:
                    if type_right.args == None:
                        self.error_logger.add(f"No se puede poner en el as un protocolo {binary_node.op.line}")
                else:
                    self.error_logger.add("en el as no hay tipo existe")

                lca = self.hierarchy.get_lca(left.type, right.type)
                if lca != None and lca.name != left.type:
                    self.error_logger.add("no se puede castear el as")
                    return ComputedValue("object", None)
                return ComputedValue(right.type)
            case "@":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type != "Number" and left.type != "String" or ight.type != "Number" and right.type != "String":
                    self.error_logger.add(f"tipo incorrecto en operacion @ {binary_node.op.line}")
                return ComputedValue("String")
            case "@@":
                left = binary_node.left.accept(self)
                right = binary_node.right.accept(self)
                if left.type != "Number" and left.type != "String" or ight.type != "Number" and right.type != "String":
                    self.error_logger.add(f"tipo incorrecto en operacion @ {binary_node.op.line}")
                return ComputedValue("String")
            
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
                if expr.type != "Boolean":
                    self.error_logger.add("no unaria not")
                else:
                    type = "Boolean"
                    if expr.value != None:
                        value = True if expr.value == False else False
            case "+":
                if expr.type != "Number":
                    self.error_logger.add("no unaria not")
                else:
                    type = "Number"
                    if expr.value != None:
                        value = expr.value
            case "-":
                if expr.type != "Number":
                    self.error_logger.add("no unaria not")
                else:
                    type = "Number"
                    if expr.value != None:
                        value = expr.value * -1
        return ComputedValue(type, value)

    def visit_literal_node(self, literal_node : LiteralNode):
        id = literal_node.id.lexeme
        match literal_node.id.type:
            case "null":
                return ComputedValue("null")
            case "false":
                return ComputedValue("Boolean", id)
            case "true":
                return ComputedValue("Boolean", id)
            case "number":
                return ComputedValue("Number", int(id))
            case "string":
                return ComputedValue("String", id)    
            case "base":
                return ComputedValue("base", "base")
            case "id":
                if id == "self":
                    self_var = self.context.get("self")
                    if self_var != None and self_var.type != "String" and self_var.value == "self":
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
                if defined != False and len(self.queue_call) > 0 and (self.queue_call[len(self.queue_call) - 1]) == "get":
                    var = self.context.get(id)
                    return ComputedValue(var.type, var.value)
                if defined != False and self.is_call_node == False:
                    var = self.context.get(id)
                    return ComputedValue(var.type, var.value)
                if self.context.is_defined_func_whithout_params(id) == True and self.is_call_node == True:
                    return ComputedValue(None, id)
                
                self.error_logger.add("variable no definida " + id)
        return ComputedValue("Object", None)




class SemanticAnalysis:
    def __init__(self) -> None:
        pass
    
    def run(self, ast):
        context = Context()
        hierarchy = Hierarchy()
        context.define_func("print", "Object", [(Token("Object", "name"), Token("Object", "Object"))])
        context.create_type("Object", [])
        context.create_type("Number", [])
        context.create_type("String", [])
        context.create_type("Boolean", [])
        context.create_type("Iterable", None, 
                            [Method("next", "Boolean", []), Method("current", "Object", [])]
                            )

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

        return err1.errors + err2.errors + err3.errors + err4.errors

 