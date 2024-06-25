from abc import ABC, abstractmethod
from common.ast_nodes.expressions import *
from common.ast_nodes.statements import *


class Visitor(ABC):
    @abstractmethod
    def visit_program_node(self, program_node : ProgramNode):
        pass
    
    @abstractmethod
    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass

    @abstractmethod
    def visit_method_node(self, method_node : MethodNode):
        pass

    @abstractmethod
    def visit_type_node(self, type_node : TypeNode):
        pass

    @abstractmethod
    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    @abstractmethod
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass

    @abstractmethod
    def visit_let_node(self, let_node : LetNode):
        pass

    @abstractmethod
    def visit_while_node(self, while_node : WhileNode):
        pass

    @abstractmethod
    def visit_for_node(self, for_node : ForNode):
        pass

    @abstractmethod
    def visit_if_node(self, if_node : IfNode):
        pass

    @abstractmethod
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass

    @abstractmethod
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    @abstractmethod
    def visit_destructor_node(self, destructor_node : DestructorNode):
        pass

    @abstractmethod
    def visit_block_node(self, block_node : BlockNode):
        pass

    @abstractmethod
    def visit_call_node(self, call_node : CallNode):
        pass

    @abstractmethod
    def visit_get_node(self, get_node : GetNode):
        pass

    @abstractmethod
    def visit_set_node(self, set_node : SetNode):
        pass

    @abstractmethod
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass

    @abstractmethod
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        pass

    @abstractmethod
    def visit_new_node(self, new_node : NewNode):
        pass

    @abstractmethod
    def visit_binary_node(self, binary_node : BinaryNode):
        pass

    
    @abstractmethod
    def visit_unary_node(self, unary_node : UnaryNode):
        pass

    @abstractmethod
    def visit_literal_node(self, literal_node : LiteralNode):
        pass

