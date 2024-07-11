.data
str0: .asciiz "Error: Index was outside of the bounds of the vector" 
type_Vector: .asciiz "Instance of type Vector" 
type_Node11235: .asciiz "Instance of type Node11235" 
type_Range: .asciiz "Instance of type Range" 
number0: .float 0.0 
number1: .float 0.0 
number2: .float 0.0 
number3: .float 1.0 
number4: .float 0.0 
number5: .float 1.0 
number6: .float 0.0 
number7: .float 1.0 
number8: .float 1.0 
number9: .float 0.0 
number10: .float 1.0 
number11: .float 0.0 
number12: .float 1.0 
number13: .float 1.0 
number14: .float 1.0 
number15: .float 0.0 
number16: .float 0.0 
number17: .float 3.141592653589793 
number18: .float 2.0 
number19: .float 0.0 
number20: .float 10.0 
number21: .float 1.0 
number22: .float 1.0 
number23: .float 2.0 
number24: .float 1.0 
number25: .float 1.0 
number26: .float 1.0 
number27: .float 2.0 
number28: .float 1.0 
number29: .float 0.0 
number30: .float 3.141592653589793 
number31: .float 1.0 
number32: .float 2.0 
number33: .float 0.0 
number34: .float 10.0 
number35: .float 1.0 
number36: .float 1.0 
number37: .float 2.0 
number38: .float 1.0 
number39: .float 2.0 
number40: .float 1.0 
number41: .float 0.0 
number42: .float 0.0 
number43: .float 0.0 
number44: .float 2.0 
number45: .float 2.0 
number46: .float 0.000001 
number47: .float 1.0 
number48: .float 1.0 


.text
.globl build_Vector
.globl length_Vector
.globl getNodeAt_Vector
.globl element_Vector
.globl set_Vector
.globl next_Vector
.globl current_Vector
.globl getValue_Node11235
.globl build_Node11235
.globl setValue_Node11235
.globl getNext_Node11235
.globl getPrevious_Node11235
.globl setNext_Node11235
.globl setPrevious_Node11235
.globl floor
.globl build_Range
.globl next_Range
.globl current_Range
.globl range
.globl floatMod
.globl sin
.globl cos
.globl abss
.globl sqrt

# j main # Simulation code

build_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lwc1 $f12 number0
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lwc1 $f12 number1
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 20($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

length_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

append_Vector:
    addi $sp $sp -20
    sw $ra 4($sp)

    li $a0 16
    li $v0 9
    syscall
    li $t0 5
    sw $t0 ($v0) # Store type metadata
    
    move $a0 $v0
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal build_Node11235
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $t0 16($sp)
    lw $a0 12($t0)
    jal stack_push

    lwc1 $f12 number2
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    lw $t0 ($s3)
    lw $t1 ($s2)
    bne $t0 $t1 equality_false_0

    seq $s0 $s0 $s1
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j equality_end_0

    equality_false_0:
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    equality_end_0:

    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_0_append_Vector

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 16($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 16($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    j conditional_end_0_append_Vector

    conditional_else_0_append_Vector:

    lw $a0 8($sp)
    jal stack_push

    lw $t0 16($sp)
    lw $a0 8($t0)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal setPrevious_Node11235
    move $a0 $v0
    jal stack_push
    j call_end_setPrevious_0

    jal method_error

    call_end_setPrevious_0:

    jal stack_pop

    lw $t0 16($sp)
    lw $a0 8($t0)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal setNext_Node11235
    move $a0 $v0
    jal stack_push
    j call_end_setNext_1

    jal method_error

    call_end_setNext_1:

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 16($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    conditional_end_0_append_Vector:

    jal stack_pop

    lw $t0 16($sp)
    lw $a0 12($t0)
    jal stack_push

    lwc1 $f12 number3
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 16($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 20
    jr $ra

getNodeAt_Vector:
    addi $sp $sp -24
    sw $ra 4($sp)

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -4($sp)

    jal floor

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 16($sp)
    jal stack_push
    
    jal stack_pop

    lw $a0 16($sp)
    jal stack_push

    lwc1 $f12 number4
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    lw $a0 16($sp)
    jal stack_push

    lw $t0 20($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add $s0 $s0 $s1
    sgt $s0 $s0 $zero
    beq $s0 1 or_true_0
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j or_end_0
    or_true_0:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    or_end_0:

    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_1_getNodeAt_Vector

    la $a0 str0
    jal build_str
    move $a0 $v0
    jal stack_push            

    jal stack_pop
    sw $v0 -4($sp)

    lw $t0 ($v0)
    li $t1 0
    beq $t0 $t1 go_print_bool_0
    li $t1 1
    beq $t0 $t1 go_print_number_0
    li $t1 2
    beq $t0 $t1 go_print_str_0
    li $t1 4
    beq $t0 $t1 go_print__Vector_0

    li $t1 5
    beq $t0 $t1 go_print__Node11235_0

    li $t1 6
    beq $t0 $t1 go_print__Range_0

    j error

    go_print_bool_0:
    jal print_bool
    j go_print_end_0

    go_print_number_0:
    jal print_number
    j go_print_end_0

    go_print_str_0:
    jal print_str
    j go_print_end_0
    go_print__Vector_0:
    la $a0 type_Vector
    jal print_pointer
    j go_print_end_0

    go_print__Node11235_0:
    la $a0 type_Node11235
    jal print_pointer
    j go_print_end_0

    go_print__Range_0:
    la $a0 type_Range
    jal print_pointer
    j go_print_end_0

    go_print_end_0:
    move $a0 $v0
    jal stack_push

    jal stack_pop

    li $a0 16
    li $v0 9
    syscall
    li $t0 5
    sw $t0 ($v0) # Store type metadata
    
    move $a0 $v0
    jal stack_push

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal build_Node11235
    move $a0 $v0
    jal stack_push

    j conditional_end_1_getNodeAt_Vector

    conditional_else_1_getNodeAt_Vector:

    lwc1 $f12 number5
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)

    li $a0 16
    li $v0 9
    syscall
    li $t0 5
    sw $t0 ($v0) # Store type metadata
    
    move $a0 $v0
    jal stack_push

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal build_Node11235
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 12($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_0
    j while_body_0
    while_start_0:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_0
    jal stack_pop
    while_body_0:

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 number6
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_2_getNodeAt_Vector

    lw $t0 20($sp)
    lw $a0 4($t0)
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)
    jal stack_push
    
    j conditional_end_2_getNodeAt_Vector

    conditional_else_2_getNodeAt_Vector:

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getNext_Node11235
    move $a0 $v0
    jal stack_push
    j call_end_getNext_2

    jal method_error

    call_end_getNext_2:

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)
    jal stack_push
    
    conditional_end_2_getNodeAt_Vector:

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 number7
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)
    jal stack_push
    
    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    j while_start_0
    while_null_end_0:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_0:

    conditional_end_1_getNodeAt_Vector:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 24
    jr $ra

element_Vector:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getNodeAt_Vector
    move $a0 $v0
    jal stack_push
    j call_end_getNodeAt_3

    jal method_error

    call_end_getNodeAt_3:

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getValue_Node11235
    move $a0 $v0
    jal stack_push
    j call_end_getValue_4

    jal method_error

    call_end_getValue_4:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

set_Vector:
    addi $sp $sp -24
    sw $ra 4($sp)

    lw $a0 20($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getNodeAt_Vector
    move $a0 $v0
    jal stack_push
    j call_end_getNodeAt_5

    jal method_error

    call_end_getNodeAt_5:

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 8($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal setValue_Node11235
    move $a0 $v0
    jal stack_push
    j call_end_setValue_6

    jal method_error

    call_end_setValue_6:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 24
    jr $ra

next_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    lwc1 $f12 number8
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_3_next_Vector

    lwc1 $f12 number9
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push

    j conditional_end_3_next_Vector

    conditional_else_3_next_Vector:

    lw $a0 8($sp)
    jal stack_push

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal element_Vector
    move $a0 $v0
    jal stack_push
    j call_end_element_7

    jal method_error

    call_end_element_7:

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 20($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    lwc1 $f12 number10
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 8($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push

    conditional_end_3_next_Vector:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

current_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 20($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

build_Node11235:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

getValue_Node11235:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 4($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

setValue_Node11235:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

getNext_Node11235:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

getPrevious_Node11235:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 8($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

setNext_Node11235:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

setPrevious_Node11235:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

floor:
    addi $sp $sp -16
    sw $ra 4($sp)

    lwc1 $f12 number11
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 8($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_1
    j while_body_1
    while_start_1:

    lw $a0 8($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_1
    jal stack_pop
    while_body_1:

    lw $a0 8($sp)
    jal stack_push

    lwc1 $f12 number12
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)
    jal stack_push
    
    j while_start_1
    while_null_end_1:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_1:

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_4_floor

    lw $a0 8($sp)
    jal stack_push

    lwc1 $f12 number13
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)
    jal stack_push
    
    j conditional_end_4_floor

    conditional_else_4_floor:

    lw $a0 8($sp)
    jal stack_push

    conditional_end_4_floor:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

build_Range:
    addi $sp $sp -24
    sw $ra 4($sp)

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 20($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    lw $t0 20($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 16($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 20($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 20($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 20($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 24
    jr $ra

next_Range:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 8($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    lw $t0 8($sp)
    lw $a0 8($t0)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

current_Range:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

range:
    addi $sp $sp -16
    sw $ra 4($sp)

    li $a0 20
    li $v0 9
    syscall
    li $t0 6
    sw $t0 ($v0) # Store type metadata
    
    move $a0 $v0
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    lwc1 $f12 number14
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    sw $v0 -16($sp)

    jal stack_pop
    sw $v0 -12($sp)

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal build_Range
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

floatMod:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 number15
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_5_floatMod

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_2
    j while_body_2
    while_start_2:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_2
    jal stack_pop
    while_body_2:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)
    jal stack_push
    
    j while_start_2
    while_null_end_2:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_2:

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    j conditional_end_5_floatMod

    conditional_else_5_floatMod:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_3
    j while_body_3
    while_start_3:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_3
    jal stack_pop
    while_body_3:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)
    jal stack_push
    
    j while_start_3
    while_null_end_3:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_3:

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_6_floatMod

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)
    jal stack_push
    
    j conditional_end_6_floatMod

    conditional_else_6_floatMod:

    lw $a0 12($sp)
    jal stack_push

    conditional_end_6_floatMod:

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    conditional_end_5_floatMod:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

sin:
    addi $sp $sp -48
    sw $ra 4($sp)

    lwc1 $f12 number16
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 40($sp)

    lwc1 $f12 number17
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 36($sp)

    lw $a0 44($sp)
    jal stack_push

    lwc1 $f12 number18
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 36($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal floatMod

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 32($sp)

    lw $a0 32($sp)
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 44($sp)
    jal stack_push
    
    jal stack_pop

    lwc1 $f12 number19
    jal build_number
    move $a0 $v0
    jal stack_push

    lwc1 $f12 number20
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal range

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 28($sp)

    lw $a0 28($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_8

    jal method_error

    call_end_next_8:

    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_4
    j while_body_4
    while_start_4:

    lw $a0 28($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_9

    jal method_error

    call_end_next_9:

    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_4
    jal stack_pop
    while_body_4:

    lw $a0 28($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal current_Range
    move $a0 $v0
    jal stack_push
    j call_end_current_10

    jal method_error

    call_end_current_10:

    jal stack_pop
    move $a0 $v0
    sw $a0 24($sp)

    lwc1 $f12 number21
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 20($sp)

    lwc1 $f12 number22
    jal build_number
    move $a0 $v0
    jal stack_push

    lwc1 $f12 number23
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 24($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    lwc1 $f12 number24
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal range

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 16($sp)

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_11

    jal method_error

    call_end_next_11:

    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_5
    j while_body_5
    while_start_5:

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_12

    jal method_error

    call_end_next_12:

    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_5
    jal stack_pop
    while_body_5:

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal current_Range
    move $a0 $v0
    jal stack_push
    j call_end_current_13

    jal method_error

    call_end_current_13:

    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)

    lw $a0 20($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 number25
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 20($sp)
    jal stack_push
    
    j while_start_5
    while_null_end_5:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_5:

    jal stack_pop

    lwc1 $f12 number26
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 24($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal power
    mov.s $f12 $f0
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 44($sp)
    jal stack_push

    lwc1 $f12 number27
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 24($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    lwc1 $f12 number28
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal power
    mov.s $f12 $f0
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    lw $a0 20($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 40($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 40($sp)
    jal stack_push
    
    j while_start_4
    while_null_end_4:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_4:

    jal stack_pop

    lw $a0 40($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 48
    jr $ra

cos:
    addi $sp $sp -52
    sw $ra 4($sp)

    lwc1 $f12 number29
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 44($sp)

    lwc1 $f12 number30
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 40($sp)

    lwc1 $f12 number31
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 36($sp)

    lw $a0 48($sp)
    jal stack_push

    lwc1 $f12 number32
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 40($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal floatMod

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 32($sp)

    lw $a0 32($sp)
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 48($sp)
    jal stack_push
    
    jal stack_pop

    lwc1 $f12 number33
    jal build_number
    move $a0 $v0
    jal stack_push

    lwc1 $f12 number34
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal range

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 28($sp)

    lw $a0 28($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_14

    jal method_error

    call_end_next_14:

    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_6
    j while_body_6
    while_start_6:

    lw $a0 28($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_15

    jal method_error

    call_end_next_15:

    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_6
    jal stack_pop
    while_body_6:

    lw $a0 28($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal current_Range
    move $a0 $v0
    jal stack_push
    j call_end_current_16

    jal method_error

    call_end_current_16:

    jal stack_pop
    move $a0 $v0
    sw $a0 24($sp)

    lwc1 $f12 number35
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 20($sp)

    lwc1 $f12 number36
    jal build_number
    move $a0 $v0
    jal stack_push

    lwc1 $f12 number37
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 24($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal range

    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 16($sp)

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_17

    jal method_error

    call_end_next_17:

    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_7
    j while_body_7
    while_start_7:

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal next_Range
    move $a0 $v0
    jal stack_push
    j call_end_next_18

    jal method_error

    call_end_next_18:

    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_7
    jal stack_pop
    while_body_7:

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal current_Range
    move $a0 $v0
    jal stack_push
    j call_end_current_19

    jal method_error

    call_end_current_19:

    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)

    lw $a0 20($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 number38
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 20($sp)
    jal stack_push
    
    j while_start_7
    while_null_end_7:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_7:

    jal stack_pop

    lw $a0 36($sp)
    jal stack_push

    lw $a0 48($sp)
    jal stack_push

    lwc1 $f12 number39
    jal build_number
    move $a0 $v0
    jal stack_push

    lw $a0 24($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal power
    mov.s $f12 $f0
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    lw $a0 20($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 44($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 44($sp)
    jal stack_push
    
    jal stack_pop

    lw $a0 36($sp)
    jal stack_push

    lwc1 $f12 number40
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 36($sp)
    jal stack_push
    
    j while_start_6
    while_null_end_6:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_6:

    jal stack_pop

    lw $a0 44($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 52
    jr $ra

abss:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    lwc1 $f12 number41
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_7_abss

    lw $a0 8($sp)
    jal stack_push

    j conditional_end_7_abss

    conditional_else_7_abss:

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push

    conditional_end_7_abss:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

sqrt:
    addi $sp $sp -24
    sw $ra 4($sp)

    lw $a0 20($sp)
    jal stack_push

    lwc1 $f12 number42
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_8_sqrt

    lwc1 $f12 number43
    jal build_number
    move $a0 $v0
    jal stack_push

    j conditional_end_8_sqrt

    conditional_else_8_sqrt:

    lw $a0 20($sp)
    jal stack_push

    lwc1 $f12 number44
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 16($sp)

    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)

    lw $a0 12($sp)
    jal stack_push

    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    lw $t0 ($s3)
    lw $t1 ($s2)
    bne $t0 $t1 equality_false_1

    seq $s0 $s0 $s1
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j equality_end_1

    equality_false_1:
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    equality_end_1:

    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_8
    j while_body_8
    while_start_8:

    lw $a0 12($sp)
    jal stack_push

    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    lw $t0 ($s3)
    lw $t1 ($s2)
    bne $t0 $t1 equality_false_2

    seq $s0 $s0 $s1
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j equality_end_2

    equality_false_2:
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    equality_end_2:

    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_8
    jal stack_pop
    while_body_8:

    lw $a0 16($sp)
    jal stack_push

    lw $a0 20($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    lwc1 $f12 number45
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 8($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    sw $v0 -4($sp)

    jal abss

    move $a0 $v0
    jal stack_push

    lwc1 $f12 number46
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_9_sqrt

    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)
    jal stack_push
    
    j conditional_end_9_sqrt

    conditional_else_9_sqrt:

    lwc1 $f12 number47
    jal build_number
    move $a0 $v0
    jal stack_push

    conditional_end_9_sqrt:

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 16($sp)
    jal stack_push
    
    j while_start_8
    while_null_end_8:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_8:

    jal stack_pop

    lw $a0 16($sp)
    jal stack_push

    conditional_end_8_sqrt:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 24
    jr $ra