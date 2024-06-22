.data
nl: .asciiz "\n"

.text
.globl print_number
.globl print_string
# .globl done # Simulation code

print_number:
	move $t0 $a0
	la $a0 nl
	li $v0 4
	syscall 
	
	move $a0 $t0
	li $v0 1
	syscall
	
	la $a0 nl
	li $v0 4
	syscall
	
	jr $ra
	
print_string:
	move $t0 $a0
	la $a0 nl
	li $v0 4
	syscall 
	
	move $a0 $t0
	li $v0 4
	syscall
	
	la $a0 nl
	li $v0 4
	syscall
	
	jr $ra

# done: # Simulation code
