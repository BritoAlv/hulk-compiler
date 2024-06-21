from abc import ABC, abstractmethod
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode


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