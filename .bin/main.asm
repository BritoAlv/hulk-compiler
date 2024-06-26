
.data
str0: .asciiz "\n"Viva Cuba Libre!"\n" 


.text
# j main # Simulation code

main:
    addi $sp $sp -8
    sw $ra 4($sp)

    jal stack_initialize

    la $a0 str0
    jal build_str
    move $a0 $v0
    jal stack_push            

    jal stack_pop
    sw $v0 -4($sp)
    
    jal print_str

    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 8
    jr $ra
    
    # j done # Simulation code
    

