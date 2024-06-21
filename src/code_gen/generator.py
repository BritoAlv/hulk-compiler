from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
from common.visitor import Visitor


WORD_SIZE = 4

class GenerationResult:
    def __init__(self, code : str, type : str = None) -> None:
        self.code = code
        self.type = type

class Generator(Visitor):
    def __init__(self, resolver : Resolver) -> None:
        self._resolver = resolver
        self._on_function_block = False
        self._func_name : str = None
        self._literal_strings : list[str] = []

    def generate(self, program : ProgramNode) -> str:
        result = self._generate(program)
        return result.code
    
    def visit_program_node(self, program_node: ProgramNode):
        code = '''
.text
# j main # Simulation code
'''
        for decl in program_node.decls:
            code += self._generate(decl).code
        
        return GenerationResult(code)
    
    def visit_method_node(self, method_node: MethodNode) -> GenerationResult:
        func_name = method_node.id.lexeme

        self._func_name = func_name
        self._resolver.start(func_name)
        stack_size = self._resolver.var_count * WORD_SIZE + 2 * WORD_SIZE

        code = f'''
{func_name}:
    addi $sp $sp -{stack_size}
    sw $ra 4($sp)
'''
        
        if func_name == 'main':
            code += '''
    jal stack_initialize
'''
        
        self._on_function_block = True
        result = self._generate(method_node.body)
        code += result.code

        code += f'''
    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp {stack_size}
    jr $ra
'''
        
        if func_name == 'main':
            code += '''    
    # j done # Simulation code
    \n
'''
        return GenerationResult(code, result.type)
    
    def visit_block_node(self, block_node: BlockNode):
        code = ''
        type = None

        for expr in block_node.exprs:
            result = self._generate(expr)
            code += result.code
            type = result.type

        return GenerationResult(code, type)
    
    def visit_let_node(self, let_node: LetNode):
        self._next_context() # Move to next context, since it's a let-node

        code = ''
        for var, value in let_node.assignments:
            var_name = var.lexeme
            offset = self._get_offset(var_name)

            result = self._generate(value)
            code += result.code

            # Update variable's type (Assuming type-checking has been correctly done previously)
            self._resolver.resolve(var_name).type = result.type

            code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''
        result = self._generate(let_node.body)
        code += result.code
        type = result.type

        return GenerationResult(code, type)

    def visit_destructor_node(self, destructor_node: DestructorNode):
        var_name = destructor_node.id.lexeme
        offset = self._get_offset(var_name)

        # We won't update type since we're assuming type-checking was already performed
        result = self._generate(destructor_node.expr)
        code = result.code

        code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
    move $a0 $v0
    jal stack_push
'''
        return GenerationResult(code, result.type)

    def visit_call_node(self, call_node: CallNode):
        code = ''

        # We won't verify that length of args match length of params, previous semantic analysis assumed
        i = 1
        for arg in call_node.args:
            result = self._generate(arg)
            code += result.code
            offset = -(i * WORD_SIZE)
            code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''
            i += 1

        if isinstance(call_node.callee, LiteralNode):
            func_name = call_node.callee.id.lexeme
            code += f'''
    jal {func_name}
    move $a0 $v0
    jal stack_push
'''
            
        type = self._resolver.get_func_type(self._func_name)
        return GenerationResult(code, type)
    
    def visit_literal_node(self, literal_node: LiteralNode):
        # TODO Put string into static data (.data)

        if literal_node.id.type == 'number':
            value = literal_node.id.lexeme
            code = f'''
    li $a0 {value}
    jal stack_push
'''         
            return GenerationResult(code, 'number')
        elif literal_node.id.type == 'id':
            var_name = literal_node.id.lexeme
            offset = self._get_offset(var_name)
            code = f'''
    lw $a0 {offset}($sp)
    jal stack_push
'''
            type = self._resolver.resolve(var_name).type
            return GenerationResult(code, type)
        elif literal_node.id.type == 'string':
            index = len(self._literal_strings)
            str_literal = literal_node.id.lexeme
            self._literal_strings.append(str_literal)
            code = f'''
    la $a0 str{index}
    jal stack_push            
'''
            return GenerationResult(code, 'string')
        
    def visit_binary_node(self, binary_node: BinaryNode):
        left_result = self._generate(binary_node.left)
        right_result = self._generate(binary_node.right)
        code = left_result.code
        code += right_result.code
        code += '''
    jal stack_pop
    move $s0 $v0
    jal stack_pop
    move $s1 $v0
        '''

        if binary_node.op.type == 'plus':
            code += '''
    add $s0 $s0 $s1
    move $a0 $s0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        elif binary_node.op.type == 'minus':
            code += '''
    sub $s0 $s0 $s1
    move $a0 $s0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        elif binary_node.op.type == 'star':
            code +='''
    mult $s0 $s1
    mflo $s0
    move $a0 $s0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        elif binary_node.op.type == 'div':
            code +='''
    div $s0 $s1
    mflo $s0
    move $a0 $s0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        else:
            raise Exception("Invalid operation")

    def visit_type_node(self, type_node: TypeNode):
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
    
    def _generate(self, stmt : Statement) -> GenerationResult:
        return stmt.accept(self)
        
    def _get_offset(self, var_name: str) -> int:
        return ((self._resolver.var_count + 2) * WORD_SIZE) - ((self._resolver.resolve(var_name).index + 1) * WORD_SIZE)
    
    def _next_context(self):
        if not self._on_function_block:
            self._resolver.next()
        else:
            self._on_function_block = False