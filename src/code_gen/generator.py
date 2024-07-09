from code_gen.environment import BOOL_TYPE_ID, NUMBER_TYPE_ID, OBJ_TYPE_ID, STR_TYPE_ID
from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, UnaryNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
from common.token_class import Token
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
        self._in_type = False
        self._in_call = False
        self._func_name : str = None
        self._type_name : str = None

        self._literal_strings : list[str] = []
        self._literal_numbers : list[str] = []

        self._if_index = 0
        self._logical_index = 0
        self._while_index = 0
        self._call_index = 0
        self._print_index = 0
        self._equality_index = 0
        self._concat_index = 0

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

        static_data_code = '''
.data
'''
        # Add static data
        i = 0
        for str_literal in self._literal_strings:
            static_data_code += f'str{i}: .asciiz {str_literal} \n' 
            i += 1

        i = 0
        for number_literal in self._literal_numbers:
            static_data_code += f'number{i}: .float {number_literal} \n' 
            i += 1
        static_data_code += '\n'

        return GenerationResult(static_data_code + code)
    
    def visit_method_node(self, method_node: MethodNode) -> GenerationResult:
        func_name = method_node.id.lexeme
        
        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._func_name = func_name
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        stack_size = func_data.var_count * WORD_SIZE + 2 * WORD_SIZE

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
        self._func_name = None # Restore to None since we're exiting the node
        return GenerationResult(code, result.type)
    
    def visit_block_node(self, block_node: BlockNode):
        code = ''
        type = None

        for i, expr in enumerate(block_node.exprs):
            result = self._generate(expr)
            code += result.code

            # Pop all the expression results previous to the last one
            if i < len(block_node.exprs) - 1:
                code += '''
    jal stack_pop
'''
            type = result.type

        return GenerationResult(code, type)
    
    def visit_let_node(self, let_node: LetNode):
        self._resolver.next() # Move to next context
        code = ''
        for assignment in let_node.assignments:
            var_name = assignment.id.lexeme
            value = assignment.body
            offset = self._get_offset(var_name)

            result = self._generate(value)
            code += result.code

            # self._resolver.resolve_var_data(var_name).type = result.type # TODO: Remove when types are correctly inferred during semantic analysis

            code += f'''
    jal stack_pop
    move $a0 $v0
    sw $a0 {offset}($sp)
'''
                
        result = self._generate(let_node.body)

        code += result.code
        type = result.type

        self._resolver.next() # Move to next context
        return GenerationResult(code, type)

    def visit_destructor_node(self, destructor_node: DestructorNode):
        var_name = destructor_node.id.lexeme
        offset = self._get_offset(var_name)

        # We won't update type since we're assuming type-checking was already performed
        result = self._generate(destructor_node.expr)
        code = result.code
        
        code += f'''
    jal stack_pop
    move $a0 $v0
    sw $a0 {offset}($sp)
    jal stack_push
    '''

        return GenerationResult(code, result.type)

    def visit_call_node(self, call_node: CallNode):
        # Function call
        if isinstance(call_node.callee, LiteralNode) and call_node.callee.id.lexeme != 'base':
            func_name = call_node.callee.id.lexeme
            code = ''
            arg_types = []

            for arg in call_node.args:
                result = self._generate(arg)
                code += result.code
                arg_types.append(result.type)

            for i in reversed(range(1, len(call_node.args) + 1)):
                offset = -(i * WORD_SIZE)
                code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''

            # Handle print particular case
            if func_name == 'print':
                code += f'''
    lw $t0 ($v0)
    li $t1 {BOOL_TYPE_ID}
    beq $t0 $t1 go_print_bool_{self._print_index}
    li $t1 {NUMBER_TYPE_ID}
    beq $t0 $t1 go_print_number_{self._print_index}
    li $t1 {STR_TYPE_ID}
    beq $t0 $t1 go_print_str_{self._print_index}
    j go_print_pointer_{self._print_index}

    go_print_bool_{self._print_index}:
    jal print_bool
    j go_print_end_{self._print_index}

    go_print_number_{self._print_index}:
    jal print_number
    j go_print_end_{self._print_index}

    go_print_str_{self._print_index}:
    jal print_str
    j go_print_end_{self._print_index}

    go_print_pointer_{self._print_index}:
    jal print_pointer
    j go_print_end_{self._print_index}
    go_print_end_{self._print_index}:
    move $a0 $v0
    jal stack_push
'''
                self._print_index += 1
                return GenerationResult(code, 'Object')
            elif func_name == 'error':
                func_type = 'error'
            else:
                func_type = self._resolver.resolve_function_data(func_name).type
            
            code += f'''
    jal {func_name}
'''
            code += '''
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, func_type)
        # Method call
        else:
            called_method = call_node.callee.id.lexeme
            if isinstance(call_node.callee, LiteralNode) and called_method == 'base':
                type_data = self._resolver.resolve_type_data(self._type_name)
                self_offset = self._get_offset('self')
                code = f'''
    lw $a0 {self_offset}($sp)
    jal stack_push
    '''
                # Remove type name attached to method name
                func_name = self._func_name
                if self._in_type:
                    func_name = self._func_name[0 : self._func_name.rfind('_')]

                method_name = type_data.methods[func_name][1]
            elif isinstance(call_node.callee, GetNode):
                self._in_call = True
                result = self._generate(call_node.callee)
                self._in_call = False

                type_data = self._resolver.resolve_type_data(result.type)
                code = result.code

                if called_method in type_data.methods:
                    method_name = type_data.methods[called_method][0]
                else:
                    method_name = None
            else:
                raise Exception("Functions are not a type here, cannot be called that way")
            
            # Generate code for arguments
            for arg in call_node.args:
                result = self._generate(arg)
                code += result.code
            
            for i in reversed(range(1, len(call_node.args) + 2)):
                offset = -(i * WORD_SIZE)
                if i > 1:
                    code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''
                else:
                    code += f'''
    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 {offset}($sp)
'''
                    
            # Check if it's not a base() call
            if isinstance(call_node.callee, GetNode):
                # Dynamic method dispatch
                for descendant in type_data.descendants:
                    descendant_type_data = self._resolver.resolve_type_data(descendant)
                    if called_method not in descendant_type_data.methods:
                        continue
                    descendant_method_name = descendant_type_data.methods[called_method][0]
                    code += f'''
    # Dynamic method dispatch
    lw $t0 ($v0)
    li $t1 {descendant_type_data.id}
    beq $t0 $t1 call_{descendant_method_name}{descendant}_{self._call_index}
    j call_next_{descendant_method_name}{descendant}_{self._call_index}
    call_{descendant_method_name}{descendant}_{self._call_index}:
    jal {descendant_method_name}
    move $a0 $v0
    jal stack_push
    j call_end_{called_method}_{self._call_index}
    call_next_{descendant_method_name}{descendant}_{self._call_index}:
    '''
                
            if method_name != None:
                code += f'''
    jal {method_name}
    move $a0 $v0
    jal stack_push
    j call_end_{called_method}_{self._call_index}
'''
        
            if isinstance(call_node.callee, GetNode):
                code += '''
    jal method_error
'''

            code += f'''
    call_end_{called_method}_{self._call_index}:
'''
            self._call_index += 1
            
            if method_name != None:
                func_data = self._resolver.resolve_function_data(method_name)
                return GenerationResult(code, func_data.type)
            
            return GenerationResult(code, 'Object')
    
    def visit_literal_node(self, literal_node: LiteralNode):

        if literal_node.id.type == 'number':
            index = len(self._literal_numbers)
            number_literal = literal_node.id.lexeme

            if '.' not in number_literal:
                number_literal += '.0'

            self._literal_numbers.append(number_literal)
            code = f'''
    lwc1 $f12 number{index}
    jal build_number
    move $a0 $v0
    jal stack_push
'''         
            return GenerationResult(code, 'Number')
        
        elif literal_node.id.type == 'id':
            var_name = literal_node.id.lexeme
            offset = self._get_offset(var_name)
            type = self._resolver.resolve_var_data(var_name).type

            code = f'''
    lw $a0 {offset}($sp)
    jal stack_push
'''
            return GenerationResult(code, type)
        
        elif literal_node.id.type == 'string':
            index = len(self._literal_strings)
            str_literal = literal_node.id.lexeme
            self._literal_strings.append(str_literal)
            code = f'''
    la $a0 str{index}
    jal build_str
    move $a0 $v0
    jal stack_push            
'''
            return GenerationResult(code, 'String')
        
        elif literal_node.id.type == 'true':
            code = '''
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Boolean')
        elif literal_node.id.type == 'false':
            code = '''
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Boolean')
        elif literal_node.id.type == 'null':
            code = f'''
    jal build_null
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Object')
        
    def visit_binary_node(self, binary_node: BinaryNode):
        left_result = self._generate(binary_node.left)

        if binary_node.op.type == 'isOp' and isinstance(binary_node.right, LiteralNode) and binary_node.right.id.type == 'id':
            type_name = binary_node.right.id.lexeme
            type_data = self._resolver.resolve_type_data(type_name)
            type_id = type_data.id
            
            code = left_result.code

            code += f'''
    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    li $s2 0
    lw $s0 ($v0)
    li $s1 {type_id}
    seq $s1 $s0 $s1
    add $s2 $s2 $s1
'''

            for descendant in type_data.descendants:
                descendant_type_data = self._resolver.resolve_type_data(descendant)
                descendant_type_id = descendant_type_data.id
                code += f'''
    li $s1 {descendant_type_id}
    seq $s1 $s0 $s1
    add $s2 $s2 $s1
'''

            code += f'''
    move $a0 $s2
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Boolean')
        elif binary_node.op.type == 'asOp' and isinstance(binary_node.right, LiteralNode) and binary_node.right.id.type == 'id':
            type_name = binary_node.right.id.lexeme
            type_data = self._resolver.resolve_type_data(type_name)
            type_id = type_data.id
            
            code = left_result.code

            code += f'''
    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    li $s2 0
    lw $s0 ($v0)
    li $s1 {type_id}
    seq $s1 $s0 $s1
    add $s2 $s2 $s1
'''

            for descendant in type_data.descendants:
                descendant_type_data = self._resolver.resolve_type_data(descendant)
                descendant_type_id = descendant_type_data.id
                code += f'''
    li $s1 {descendant_type_id}
    seq $s1 $s0 $s1
    add $s2 $s2 $s1
'''
                
            code += '''
    beq $s2 0 cast_error
    move $a0 $v0
    jal stack_push
'''

            return GenerationResult(code, type_name)

        right_result = self._generate(binary_node.right)

        null_check_code = '''
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error'''

        code = left_result.code
        code += right_result.code
        code += f'''
    jal stack_pop
    {null_check_code if binary_node.op.lexeme not in ['doubleEqual', 'notEqual'] else ''}
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    {null_check_code if binary_node.op.lexeme not in ['doubleEqual', 'notEqual'] else ''}
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    '''

        # Addition
        if binary_node.op.type == 'plus':
            code += '''
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Number')
        # Subtraction
        elif binary_node.op.type == 'minus':
            code += '''
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Number')
        # Multiplication
        elif binary_node.op.type == 'star':
            code +='''
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Number')
        # Division
        elif binary_node.op.type == 'div':
            code +='''
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Number')
        # Logical And and Or
        elif binary_node.op.type == 'and' or binary_node.op.type == 'or':
            if binary_node.op.type == 'and':
                code += f'''
    add $s0 $s0 $s1
    beq $s0 2 and_true_{self._logical_index}
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j and_end_{self._logical_index}
    and_true_{self._logical_index}:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    and_end_{self._logical_index}:
            '''
            else:    
                code += f'''
    add $s0 $s0 $s1
    sgt $s0 $s0 $zero
    beq $s0 1 or_true_{self._logical_index}
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j or_end_{self._logical_index}
    or_true_{self._logical_index}:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    or_end_{self._logical_index}:
'''
            self._logical_index += 1
            return GenerationResult(code, 'Boolean')
        # GreaterThan
        elif binary_node.op.type == 'greater':
            code +='''
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Boolean')
        # LessThan
        elif binary_node.op.type == 'less':
            code +='''
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Boolean')
        # GreaterThanOrEqual
        elif binary_node.op.type == 'greaterEq':
            code +='''
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Boolean')
        # LessThanOrEqual
        elif binary_node.op.type == 'lessEq':
            code +='''
    li $a0 0
    li $t0 1
    c.le.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'Boolean')
        # DoubleEqual
        elif binary_node.op.type == 'doubleEqual':
            code += f'''
    lw $t0 ($s3)
    lw $t1 ($s2)
    bne $t0 $t1 equality_false_{self._equality_index}

    seq $s0 $s0 $s1
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j equality_end_{self._equality_index}

    equality_false_{self._equality_index}:
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    equality_end_{self._equality_index}:
'''
            self._equality_index += 1
            return GenerationResult(code, 'Boolean')
        # NotEqual
        elif binary_node.op.type == 'notEqual':
            code += f'''
    lw $t0 ($s3)
    lw $t1 ($s2)
    bne $t0 $t1 equality_true_{self._equality_index}

    seq $s0 $s0 $s1
    seq $s0 $s0 0
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j equality_end_{self._equality_index}

    equality_true_{self._equality_index}:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    equality_end_{self._equality_index}:
'''
            self._equality_index += 1
            return GenerationResult(code, 'Boolean')
        # String concatenation
        elif binary_node.op.type == 'at' or binary_node.op.type == 'doubleAt':
            code += f'''
    lw $t0 ($s2)
    beq $t0 {BOOL_TYPE_ID} stringify_bool_{self._concat_index}
    beq $t0 {NUMBER_TYPE_ID} stringify_number_{self._concat_index}
    beq $t0 {STR_TYPE_ID} stringify_end_{self._concat_index}
    j stringify_pointer_{self._concat_index}

    stringify_bool_{self._concat_index}:
    move $a0 $s0
    jal bool_to_str
    move $s0 $v0
    j stringify_end_{self._concat_index}

    stringify_number_{self._concat_index}:
    mov.s $f12 $f20
    jal number_to_str
    move $s0 $v0 
    j stringify_end_{self._concat_index}

    stringify_pointer_{self._concat_index}:
    move $a0 $s0
    jal pointer_to_str
    move $s0 $v0

    stringify_end_{self._concat_index}:
'''
            self._concat_index += 1
            code += f'''
    lw $t0 ($s3)
    beq $t0 {BOOL_TYPE_ID} stringify_bool_{self._concat_index}
    beq $t0 {NUMBER_TYPE_ID} stringify_number_{self._concat_index}
    beq $t0 {STR_TYPE_ID} stringify_end_{self._concat_index}
    j stringify_pointer_{self._concat_index}

    stringify_bool_{self._concat_index}:
    move $a0 $s1
    jal bool_to_str
    move $s1 $v0
    j stringify_end_{self._concat_index}

    stringify_number_{self._concat_index}:
    mov.s $f12 $f22
    jal number_to_str
    move $s1 $v0 
    j stringify_end_{self._concat_index}

    stringify_pointer_{self._concat_index}:
    move $a0 $s1
    jal pointer_to_str
    move $s1 $v0

    stringify_end_{self._concat_index}:
'''
            self._concat_index += 1

            if binary_node.op.type == 'at':
                code += '''
    move $a0 $s1
    move $a1 $s0
    jal str_concat
    move $a0 $v0
    jal build_str
    move $a0 $v0
    jal stack_push
'''
            else:
                code += '''
    move $a0 $s1
    move $a1 $s0
    jal str_space_concat
    move $a0 $v0
    jal build_str
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'String')
        # Power
        elif binary_node.op.type == 'powerOp' or binary_node.op.type == 'modOp':
            if binary_node.op.type == 'powerOp':
                code +='''
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal power
    mov.s $f12 $f0
    jal build_number
    move $a0 $v0
    jal stack_push
'''
            else:
                code +='''
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal mod
    mov.s $f12 $f0
    jal build_number
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Number')
        else:
            raise Exception("Invalid operation")

    def visit_type_node(self, type_node: TypeNode):
        self._type_name = type_node.id.lexeme
        self._in_type = True

        code = ''
        for method in type_node.methods:
            code += self._generate(method).code

        self._type_name = None # Restore to None since we're exiting the node
        self._in_type = False # Restore to False since we're exiting the node
        return GenerationResult(code)

    def visit_protocol_node(self, protocol_node: ProtocolNode):
        pass

    def visit_attribute_node(self, attribute_node: AttributeNode):
        attribute_name = attribute_node.id.lexeme
        result = self._generate(attribute_node.body)
        code = result.code

        type_data = self._resolver.resolve_type_data(self._type_name)
        # type_data.attributes[attribute_name].type = result.type # TODO: Remove when types are correctly inferred during semantic analysis

        self_offset = self._get_offset('self')
        attribute_offset = (type_data.attributes[attribute_name].index + type_data.inherited_offset) * WORD_SIZE

        code += f'''
    jal stack_pop
    lw $t0 {self_offset}($sp)
    sw $v0 {attribute_offset}($t0)
    move $a0 $v0
    jal stack_push
'''

        return GenerationResult(code)

    def visit_signature_node(self, signature_node: SignatureNode):
        pass
    
    def visit_if_node(self, if_node: IfNode):
        if_index = self._if_index
        self._if_index += 1

        types : list[str] = []
        code = ''
        i = 0
        for condition, expr in if_node.body:
            condition_result = self._generate(condition)

            if i > 0:
                code += f'''
    conditional_{if_index}_{i - 1}_{self._func_name}:
'''
            code += condition_result.code
            code += f'''
    jal stack_pop
    lw $t0 4($v0)
'''
            if i < len(if_node.body) - 1:
                code += f'''
    bne $t0 1 conditional_{if_index}_{i}_{self._func_name}
'''
            else:
                code += f'''
    bne $t0 1 conditional_else_{if_index}_{self._func_name}
'''
            
            expr_result = self._generate(expr)
            code += expr_result.code
            types.append(expr_result.type)
            code += f'''
    j conditional_end_{if_index}_{self._func_name}
'''
            i += 1

        code += f'''
    conditional_else_{if_index}_{self._func_name}:
'''
        else_result = self._generate(if_node.elsebody)
        code += else_result.code
        types.append(else_result.type)

        code += f'''
    conditional_end_{if_index}_{self._func_name}:
'''

        # Check return type
        base_type = types[0]
        for type in types:
            if type != base_type:
                return GenerationResult(code, 'Object')
        
        return GenerationResult(code, base_type)


    def visit_while_node(self, while_node: WhileNode):
        while_index = self._while_index
        self._while_index += 1
        code = ''
        code += self._generate(while_node.condition).code
        code += f'''
    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_{while_index}
    j while_body_{while_index}
    while_start_{while_index}:
'''
        code += self._generate(while_node.condition).code
        code += f'''
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_{while_index}
    jal stack_pop
    while_body_{while_index}:
'''
        body_result = self._generate(while_node.body)
        code += body_result.code
        code += f'''
    j while_start_{while_index}
    while_null_end_{while_index}:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_{while_index}:
'''
        while_index += 1

        return GenerationResult(code, body_result.type)

    def visit_new_node(self, new_node: NewNode):
        type_name = new_node.id.lexeme
        type_data = self._resolver.resolve_type_data(type_name)
        attributes_len = len(type_data.attributes)
        type_size = type_data.inherited_offset + (attributes_len if attributes_len > 0 else 1)
        type_id = type_data.id

        code = f'''
    li $a0 {type_size * WORD_SIZE}
    li $v0 9
    syscall
    li $t0 {type_id}
    sw $t0 ($v0) # Store type metadata
    {'sw $v0 4($v0)' if attributes_len == 0 else ''}
    move $a0 $v0
    jal stack_push
'''
        
        for arg in new_node.args:
            result = self._generate(arg)
            code += result.code
            
        for i in reversed(range(1, len(new_node.args) + 2)):
            offset = -(i * WORD_SIZE)
            code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''
            
        code += f'''
    jal build_{type_name}
    move $a0 $v0
    jal stack_push
'''
        return GenerationResult(code, type_name)
    
    def visit_unary_node(self, unary_node : UnaryNode):
        result = self._generate(unary_node.expr)
        code = result.code
        if unary_node.op.type == 'not':
            code += '''
    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lw $a0 4($v0)
    li $t0 0
    seq $a0 $a0 $t0
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Boolean')
        else:
            code += '''
    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'Number')
    
    def visit_get_node(self, get_node: GetNode):
        if self._type_name != None:
            type_data = self._resolver.resolve_type_data(self._type_name)
        if isinstance(get_node.left, LiteralNode) and get_node.left.id.lexeme == 'self' and (get_node.id.lexeme not in type_data.methods or not self._in_call):
            type_data = self._resolver.resolve_type_data(self._type_name)
            if get_node.id.lexeme in type_data.attributes:
                var_data = type_data.attributes[get_node.id.lexeme]
                attribute_offset = (var_data.index + type_data.inherited_offset) * WORD_SIZE
                self_offset = self._get_offset('self')
                code = f'''
    lw $t0 {self_offset}($sp)
    lw $a0 {attribute_offset}($t0)
    jal stack_push
'''
                return GenerationResult(code, var_data.type)
            else:
                raise Exception("There's no method nor attribute called like that")
        return self._generate(get_node.left)
                
    def visit_set_node(self, set_node: SetNode):
        if isinstance(set_node.left, LiteralNode) and set_node.left.id.lexeme == 'self':
            result = self._generate(set_node.value)
            code = result.code

            type_data = self._resolver.resolve_type_data(self._type_name)
            var_data = type_data.attributes[set_node.id.lexeme]
            self_offset = self._get_offset('self')
            attribute_offset = (var_data.index + type_data.inherited_offset) * WORD_SIZE
            code += f'''
    jal stack_pop
    lw $t0 {self_offset}($sp)
    sw $v0 {attribute_offset}($t0)
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, result.type)

    def visit_explicit_vector_node(self, explicit_vector_node: ExplicitVectorNode):
        pass

    def visit_implicit_vector_node(self, implicit_vector_node: ImplicitVectorNode):
        pass

    def visit_vector_get_node(self, vector_get_node: VectorGetNode):
        node = CallNode(
            GetNode(
                vector_get_node.left,
                Token('id', 'element')
            ),
            [vector_get_node.index]
        )
        return self._generate(node)

    def visit_vector_set_node(self, vector_set_node: VectorSetNode):
        pass
    
    def _generate(self, stmt : Statement) -> GenerationResult:
        return stmt.accept(self)
        
    def _get_offset(self, var_name: str) -> int:
        func_data = self._resolver.resolve_function_data(self._func_name)

        return ((func_data.var_count + 2) * WORD_SIZE) - ((self._resolver.resolve_var_data(var_name).index + 1) * WORD_SIZE)
