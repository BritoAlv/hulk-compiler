from os import name
from sqlalchemy import false
from common.ast_nodes.expressions import *
from common.ast_nodes.expressions import VectorGetNode
from common.ast_nodes.statements import *
from common.visitor import Visitor



class Type:
    def __init__(self, name) -> None:
        self.name = name
        self.attribute = []
        self.method = []

    def get_attribute(self, name):
        for i in self.attribute:
            if i.name == name:
                return i
        return None
    
    def get_method(self, name):
        for i in self.method:
            if i.name == name:
                return i
        return None

    def define_attribute(self, name, type):
        if self.get_attribute(name) != None:
            return False
        self.attribute.append(Attribute(name, type))

    def define_method(self, name, return_type, arg, arg_types):
        if self.get_attribute(name) != None:
            return False
        self.method.append(Method(name, return_type, arg))

class Attribute:
    def __init__(self, name, itype) -> None:
        self.name = name
        self.type = itype

class Method:
    def __init__(self, name, return_type, args) -> None:
        self.name = name
        self.type = return_type
        self.args = args

class Context():
    def __init__(self , parent = None) -> None:
        self.parent = parent
        self.dict = {}
        self.function = {}
        self.types : list[Type] = []

    def is_defined(self, var) -> bool:
        return self.dict.get(var) or (self.parent != None and self.parent.is_defined(var))
    
    def is_defined_func(self, func, args) -> bool:
        if self.function.get(func) and self.function[func] == args:
            return True
        return (self.parent != None and self.parent.is_defined_func(func, args))
    
    def define(self, var) -> bool:
        if self.is_defined(var):
            return False
        self.dict[var] = True
        return True
    
    def define_func(self, var, args) -> bool:
        if self.is_defined_func(var, args):
            return False
        self.function[var] = True
        return True
    
    def create_child_context(self):
        return Context(self)
    
    def get_type(self, type_name):
        for i in self.types:
            if i.name == type_name:
                return i
    def get_type_for(self, symbol):
        pass
    def defineSymbol(self, symbol, type) -> bool:
        return False
    def create_type(self, name):
        self.types.append(Type(name))
        pass

class TypeCollectorVisitor(Visitor):
    def __init__(self, context : Context):
        self.context = context
    
    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            i.accept(self)
    
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass

    def visit_method_node(self, method_node : MethodNode):
        pass

    def visit_type_node(self, type_node : TypeNode):
        self.context.create_type(type_node.id.lexeme)            

    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        self.context.create_type(protocol_node.id.lexeme)            

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
    def __init__(self, context):
        self.context = context
    
    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            i.accept(self)
    
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass

    def visit_method_node(self, method_node : MethodNode):
        pass

    def visit_type_node(self, type_node : TypeNode):
        current_type = self.context.get_type(type_node.id.lexeme)
        for i in type_node.params:
            current_type.define_attribute(i[0])
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

    def visit_literal_node(self, literal_node : LiteralNode):
        pass
    def visit_unary_node(self, binary_node : UnaryNode):
        
        return True
    

class SemanticAnalysis:
    def __init__(self) -> None:
        pass
    
    def run(self, ast):
        
        context = Context()

        typeCollectorVisitor = TypeCollectorVisitor(context)
        typeBuilderVisitor = TypeBuilderVisitor(context)

        ast.accept(typeCollectorVisitor)
        print(ast.accept(typeBuilderVisitor))

from parsing.parser.parser import Parser
from parsing.parser_generator_lr.parsing_table import ParsingTable

tableHulk = ParsingTable.load_parsing_table("hulk_grammar")
# print(tableHulk)

node = tableHulk.parse(
    [Token(x, x, 0, 0) for x in [
        'type', 'id', 'lparen', 'id', 'colon', 'id', 'comma', 'id', 'colon', 'id', 'rparen',
        'lbrace',
            'id', 'equal', 'id', 'semicolon',
            'id', 'equal', 'id', 'semicolon',
            'id', 'equal', 'id', 'minus', 'number','semicolon',

            'id', 'lparen', 'rparen', 'colon', 'id', 'arrow', 'lparen', 'self', 'dot', 'id', 'destrucOp', 'self', 'dot', 'id', 'plus', 'number', 'rparen', 'less', 'id', 'semicolon',
        'rbrace',

        'protocol', 'id',
        'lbrace',
            'id', 'lparen', 'id', 'colon', 'id', 'rparen', 'colon', 'id', 'semicolon',
            'id', 'lparen', 'rparen', 'colon', 'id', 'semicolon',
        'rbrace',
        
        'protocol', 'id', 'extends', 'id',
        'lbrace',
            'id', 'lparen', 'id', 'colon', 'id', 'rparen', 'colon', 'id', 'semicolon',
            'id', 'lparen', 'rparen', 'colon', 'id', 'semicolon',
        'rbrace',

        'lbrace',

        'let', 'id', 'equal', 'lbracket', 'id', 'doubleOr', 'id', 'in', 'id', 'lparen', 'id', 'comma', 'id', 'rparen', 'rbracket', 'in', 'id', 'lparen', 'id', 'rparen', 'semicolon',

        'let', 'id', 'equal', 'lbracket', 'number', 'comma', 'number', 'comma', 'number', 'comma', 'number', 'comma', 'number', 'rbracket', 'in',
        'for', 'lparen', 'id', 'in', 'id', 'rparen',
            'id', 'lparen', 'id', 'rparen', 'semicolon',

        'lparen', 'id', 'rparen', 'dot', 'id', 'semicolon',

        'let', 'id', 'equal', 'new', 'id', 'lparen', 'number', 'comma', 'id', 'rparen', 'in', 'id', 'lparen', 'id', 'rparen', 'semicolon',
        'rbrace', 'semicolon',
        '$']]
)


node.root.print([0], 0, True)

context = Context()

typeCollectorVisitor = TypeCollectorVisitor(context)
typeBuilderVisitor = TypeBuilderVisitor(context)

p = Parser()

ast = p.toAst(node)

ast.accept(typeCollectorVisitor)
print(ast.accept(typeBuilderVisitor))
