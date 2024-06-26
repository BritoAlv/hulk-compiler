
from time import sleep
from sympy import false, true
from code_gen.environment import STR_TYPE_ID, Context, Environment, FunctionData, TypeData, VarData
from common.graph import Graph
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, UnaryNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, Statement, TypeNode
from common.visitor import Visitor


class EnvironmentBuilder(Visitor):
    def __init__(self) -> None:
        self._environment : Environment = None
        self._context : Context = None

        self._var_index : int = 0
        self._type_index : int = STR_TYPE_ID + 1

        self._func_name : str
        self._type_name : str
        self._in_type = False

        self._type_graph = Graph()
        self._root_types : list[str] = []

    def build(self, program: ProgramNode) -> Environment:
        self._environment = Environment()
        self._build(program)

        self._handle_inheritance()

        return self._environment

    def visit_program_node(self, program_node: ProgramNode):
        for decl in program_node.decls:
            self._build(decl)
    
    def visit_method_node(self, method_node: MethodNode):
        func_data = FunctionData()
        func_name = method_node.id.lexeme
        func_type = method_node.type.lexeme
        func_data.type = func_type

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._environment.add_function_data(func_name, func_data)
        self._var_index = 0 # Reset var_index
        self._func_name = func_name
        self._context = func_data.context

        if self._in_type:
            func_data.params['self'] = VarData(self._var_index, self._type_name)
            self._var_index += 1

        for param in method_node.params:
            param_name = param[0].lexeme
            param_type = param[1].lexeme

            if param_name in func_data.params:
                    raise Exception("Params must be named differently")
            
            func_data.params[param_name] = VarData(self._var_index, param_type)
            self._var_index += 1
                
        self._build(method_node.body)

        self._func_name = None # Restore to None since we're exiting the node
        func_data.var_count = self._var_index

    def visit_let_node(self, let_node: LetNode):
        old_context = self._create_context()
        function_data = self._environment.get_function_data(self._func_name)

        for assignment in let_node.assignments:
            var_name = assignment.id.lexeme
            value = assignment.body
            
            if var_name in self._context.variables:
                raise Exception("Cannot declare the same variable twice in the same scope")
            elif var_name in function_data.params:
                raise Exception("Variable is already used as a parameter name")
            
            self._context.variables[var_name] = VarData(self._var_index)
            self._var_index += 1
            self._build(value)

        self._build(let_node.body)

        self._context = old_context

    def visit_block_node(self, block_node: BlockNode):
        for expr in block_node.exprs:
            self._build(expr)  

    def visit_destructor_node(self, destructor_node: DestructorNode):
        self._build(destructor_node.expr)

    def visit_binary_node(self, binary_node: BinaryNode):
        left_expr = binary_node.left
        right_expr = binary_node.right

        self._build(left_expr)
        self._build(right_expr)        

    def visit_call_node(self, call_node: CallNode):
        self._build(call_node.callee)
        
        for expr in call_node.args:
            self._build(expr)

    def visit_type_node(self, type_node: TypeNode):
        type_data = TypeData(self._type_index)
        self._type_index += 1
        type_name = type_node.id.lexeme
        self._type_name = type_name
        self._in_type = True

        i = 0
        for attribute, _ in type_node.attributes:
            attribute_name = attribute.lexeme
            if attribute_name in type_data.attributes:
                raise Exception(f"Cannot declare attribute '{attribute_name}' twice")
            type_data.attributes[attribute_name] = VarData(i)
            i += 1
        
        for method in type_node.methods:
            method_name = method.id.lexeme
            if method_name in type_data.methods:
                raise Exception(f"Cannot declare method '{method_name}' twice")
            type_data.methods[method_name] = [f'{method_name}_{type_name}']

        if type_node.ancestor_id != None:
            ancestor = type_node.ancestor_id.lexeme
            type_data.ancestor = ancestor
            self._type_graph.add((ancestor, type_name))
        else:
            self._type_graph.add_vertex(type_name)
            self._root_types.append(type_name)
            

        self._environment.add_type_data(type_name, type_data)
        
        for method in type_node.methods:
            self._build(method)

        self._in_type = False # Restore to False since we're exiting the node
        self._type_name = None # Restore to None since we're exiting the node

    def visit_unary_node(self, unary_node : UnaryNode):
        pass

    def visit_protocol_node(self, protocol_node: ProtocolNode):
        pass

    def visit_attribute_node(self, attribute_node: AttributeNode):
        pass

    def visit_signature_node(self, signature_node: SignatureNode):
        pass
    
    def visit_if_node(self, if_node: IfNode):
        pass

    def visit_while_node(self, while_node: WhileNode):
        pass

    def visit_for_node(self, for_node: ForNode):
        pass

    def visit_new_node(self, new_node: NewNode):
        pass
    
    def visit_get_node(self, get_node: GetNode):
        pass

    def visit_set_node(self, set_node: SetNode):
        pass

    def visit_explicit_vector_node(self, explicit_vector_node: ExplicitVectorNode):
        pass

    def visit_implicit_vector_node(self, implicit_vector_node: ImplicitVectorNode):
        pass

    def visit_vector_get_node(self, vector_get_node: VectorGetNode):
        pass

    def visit_vector_set_node(self, vector_set_node: VectorSetNode):
        pass

    def visit_literal_node(self, literal_node: LiteralNode):
        pass

    def _build(self, stmt : Statement):
        return stmt.accept(self)
    
    def _create_context(self):
        old_context = self._context
        func_data = self._environment.get_function_data(self._func_name)

        if old_context == None:
            self._context = Context()
            func_data.context = self._context
        else:
            new_context = Context()
            new_context.parent = old_context
            old_context.children.append(new_context)
            self._context = new_context

        return old_context
    
    def _handle_inheritance(self):
        if self._type_graph.is_cyclic():
            raise Exception("Cannot have cyclic inheritance")
        
        stack : list[str] = [] + self._root_types
        graph = self._type_graph
        
        while(len(stack) > 0):
            vertex = stack.pop()
            neighbors = graph.neighbors(vertex)
            vertex_type_data = self._environment.get_type_data(vertex)

            for neighbor in neighbors:
                neighbor_type_data = self._environment.get_type_data(neighbor)
                
                # Update inherited offset to descendant types
                neighbor_type_data.inherited_offset = vertex_type_data.inherited_offset + len(vertex_type_data.attributes)

                # Update methods to descendant types
                for method in vertex_type_data.methods:
                    if method not in neighbor_type_data.methods:
                        neighbor_type_data.methods[method] = [vertex_type_data.methods[method]]
                    else:
                        neighbor_type_data.methods[method].insert(1, f'{method}_{vertex}')
                
                # Push onto stack
                stack.append(neighbor)