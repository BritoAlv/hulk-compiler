make run:
	python3 repl.py

make test:
	g++ expression-generator.cpp -o expgen.out
	echo > cases.txt $(CASES)
	./expgen.out < cases.txt > expgen.txt   
	python3 tester.py < expgen.txt > result.txt
	cat result.txt