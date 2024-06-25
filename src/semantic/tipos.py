from os import name
from sqlalchemy import false
from common.ast_nodes.expressions import *
from common.ast_nodes.statements import *
from common.visitor import Visitor

class ErrorLogger:
    def __init__(self) -> None:
        pass
    def log_error(self, msg):
        print(msg)

class Type:
    def __init__(self) -> None:
        self.name = ""
        self.attribute = []
        self.method = []

    def get_attribute(self, name):
        pass

    def get_method(self, name):
        pass

    def define_attribute(self, name, type):
        pass

    def define_method(self, name, return_type, arg, arg_types):
        pass

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
        pass
    def get_type_for(self, symbol):
        pass
    def defineSymbol(self, symbol, type) -> bool:
        return False
    def create_type(self, name):
        pass

class TypeCollectorVisitor(Visitor):
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
        self.context.create_type(type_node.id.lexeme)

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
        print(type_node)

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





from parsing.parser.parser import Parser
from parsing.parser_generator_lr.parsing_table import ParsingTable

tableHulk = ParsingTable.load_parsing_table("hulk_grammar")
# print(tableHulk)

node = tableHulk.parse(
    [Token(x, x, 0, 0) for x in [
        'lbrace',
        'let', 'id', 'colon', 'id', 'equal', 'id', 'plus', 'number', 'in', 'lparen', 'number', 'rparen', 'semicolon',
        
        'id', 'destrucOp', 'lparen', 'number', 'plus', 'number', 'rparen', 'semicolon',

        'number', 'semicolon',

        'id', 'dot', 'id', 'semicolon',

        'id', 'dot', 'id', 'dot', 'id', 'lparen', 'rparen', 'semicolon',
        'rbrace', 'semicolon',
        '$']]
)


node.root.print([0], 0, True)

# context = Context()

# typeCollectorVisitor = TypeCollectorVisitor(context)
# typeBuilderVisitor = TypeBuilderVisitor(context)

# p = Parser()

# ast = p.toAst(node)

# ast.accept(typeCollectorVisitor)
# print(ast.accept(typeBuilderVisitor))
