##
type A(id : string) 
{
    id = id;
    jump() : object => print(self.id);
    greet() : object => print("Call me" @@ self.id);
}

type B(id : string, size : number) inherits A(id)
{
    size = size;
    jump() : object => print("My size is" @@ self.size);
}

type C inherits B { }

let a = new A("Pancho"), b = new B("Jenn", 20), c = new C("John", 30) in 
{
    a.jump();
    b.jump();
    b.greet();
    c.jump();
    c.greet();
};
##

##
type Knight inherits Person {
    name() : string => "Sir" @@ base();
}

type Person(firstname : string, lastname : string) {
    firstname = firstname;
    lastname = lastname;
    ada = 43;
    name() : string => self.firstname @@ self.lastname;
    hash() : number {
        self.ada;
    };
}

let phil = new Knight("Phil", "Collins"), thomas = new Person("Thomas", "Shelby") in 
{
    print(phil.name());
    print(thomas.name());
    print(phil.hash());
    print(thomas.hash());
};
##

## 
function factorial(n : number) : number => 
if (n < 1)
    1
else
    n * factorial(n - 1);

print(factorial(5));
##

##
function fibonacci(n : number) : number => 
if (n < 2)
    1
else
    fibonacci(n - 1) + fibonacci(n - 2);

print(fibonacci(5));
##

##
function fibonacci(n : number) : number => 
let index = 0, next = 1, current = 1, temp = next, condition = true in 
    while(condition)
        if (index == n)
        {
            condition := false;
            current;
        }
        else
        {
            index := index + 1;
            temp := next;
            next := next + current;
            current := temp;
        };

print(fibonacci(40));
##

##
function fib(n : number) : number => if (n == 0 | n == 1) 1 else fib(n-1) + fib(n-2);

print(fib(6));
##

##
print(print(2)); # Prints pointer address
##

##
print(print(2) as number); # Prints 2
##

##
let a = "Thomas", a = "John" in 
{
    let a = "Shelby" in print(a);
    let b = a @@ "McArthur" in print(b);
    print(a);
};
##

##
{
    let a = 6 in
        let b = a * 7 in
            print(b);
    
    print(let b = 6 in b * 7);

    let a = 20 in {
        let a = 42 in print(a);
        print(a);
    };

    let a = 7, a = 7 * 6 in print(a);

    let a = 0 in {
        print(a);
        a := 1;
        print(a);
    };

    let a = 0 in
        let b = a := 1 in {
            print(a);
            print(b);
        };
};
##

##
type Range(start : number, end : number, offset : number) {
    start = start;
    end = end;
    current = start - offset;
    offset = offset;

    next(): bool => (self.current := self.current + self.offset) < self.end ;
    current(): number => self.current;
}

let interval = new Range(1, 5, 1) in 
{
    print(interval.next());
    print(interval.current());
    print(interval.next());
    print(interval.current());
    print(interval.next());
    print(interval.current());
    print(interval.next());
    print(interval.current());
    print(interval.next());
    print(interval.current());
    print(interval.next());
    print(interval.current());
};



let i = 0 in
while (i < 10) 
    print(i := i + 1);
##

##
type Range(start : number, end : number, offset : number) {
    start = start;
    end = end;
    current = start - offset;
    offset = offset;

    next(): bool => (self.current := self.current + self.offset) < self.end ;
    current(): number => self.current;
}

for (n in new Range(1, 10, 1)) print(n);
##

##
type Stack
{
    count = 0;
    top : Node = (while(false) 0) as Node;
    index = 0;
    currentProp = while(false) 0 as Node;

    push(value : number) : number => let node = new Node(value) in 
    {
        if (self.count == 0)
        {
            self.top := node;
            self.count := 1;
        }
        else
        {
            self.top.setNext(node);
            node.setPrevious(self.top);
            self.top := node;
            self.count := self.count + 1;
        };

        self.currentProp := self.top;
        self.index := self.count;
        value;
    };
    
    peek() : number => self.top.getValue();

    getCount() : number => self.count;

    next() : bool 
    {
        if (self.index == self.count & self.index > 0)
        {
            self.currentProp := self.top;
            self.index := self.index - 1;
            true;
        }
        elif (self.index > 0)
        {
            self.currentProp := self.currentProp.getPrevious();
            self.index := self.index - 1;
            true;
        }
        else
            false;
    }

    current() : number => self.currentProp.getValue(); 
}

type Node(value : number) 
{
    value = value;
    previous : Node = while(false) 0;
    next : Node = while(false) 0;
    getValue() : number => self.value;
    getNext() : Node => self.next;
    getPrevious() : Node => self.previous;
    setNext(node : Node) : Node => self.next := node;
    setPrevious(node : Node) : Node => self.previous := node;
}

let s = new Stack() in 
{
    s.push(1);
    s.push(2);
    s.push(3);
    
    for (elem in s) 
        print(elem);

    print("\n");

    s.push(10);
    s.push(25);
    s.push(100);

    for (elem in s) 
        print(elem);
};
##

##
type Node(value : number)
{
    value = value;
    previous = 0 as object;
    next = 0 as object;
    getValue() : number => self.value;
    setPrevious(node : Node) : Node => self.previous := node; 
    getPrevious() : Node => self.previous;
}

{
    print(("Casa" as bool) is string);
    print(("Casa" as bool) is bool);

    let node = new Node(40), previous = node.getPrevious() in 
    {
        if (previous is Node)
            print(previous.getValue())
        else
            print("Null pointer");
        
        previous := node.setPrevious(new Node(30));

        if (previous is Node)
            print(previous.getValue())
        else
            print("Null pointer");
        
        print(node.getValue());
    };
};
##

##
type Node(value : number) 
{
    value = value;
    previous = while(false) 0;
    getPrevious() : Node => self.previous;
    setPrevious(node : Node) : Node => self.previous := node;
    getValue() : number => self.value;
}

let a = new Node(10) in 
{
    a.setPrevious(new Node(20));
    print(a.getValue());
    print(a.getPrevious().getValue());
    a.getPrevious().getPrevious().getValue(); # Null reference error
};
##

##
type A
{
    casa() : object => print("A");
}

type B inherits A
{
    casa() : object => print("B");
}

type C inherits B
{
    casa() : object => print("C");
}

function Test(n : number) : A =>
if (n < 0)
    new C()
elif (n < 10)
    new B()
else
    new A();

let a = Test(10), b = Test(5), c = Test(-10) in {
    a.casa();
    b.casa();
    c.casa();
};
##

##
type Stack
{
    top = new Node(0);
    count = 0;

    push(n : number) : number => let pushedNode = new Node(n) in 
    {
        pushedNode.addPrevious(self.top);
        self.top.addNext(pushedNode);
        self.top := pushedNode;
        self.count := self.count + 1;
        n;
    };

    pop(n : number) : number => let popped = self.top.getValue() in 
    {
        self.top := self.top.getPrevious();
        self.count := self.count - 1;
        popped;
    };

    peek() : number => self.top.getValue();

    getCount() : number => self.count;
}

type Node(value : number)
{
    value = value;
    previous = self;
    next = self;
    addPrevious(previous : Node) : Node => self.previous := previous;
    addNext(next : Node) : Node => self.next := next;
    getPrevious() : Node => self.previous;
    getNext() : Node => self.next;
    print() : number => print(self.value);
    getValue() : number => self.value;
}

let stack = new Stack() in
{
    stack.push(4);
    print("Top:" @@ stack.peek());
    print("Count:" @@ stack.getCount());
    stack.push(3);
    stack.pop();
    stack.push(2);
    stack.push(5);
    stack.pop();
    stack.pop();
    print("Top:" @@ stack.peek());
    print("Count:" @@ stack.getCount());
    stack.push(10);
    print("Top:" @@ stack.peek());
    print("Count:" @@ stack.getCount());
};
##

##

let a = "Thomas" in 
{
    let a = a @@ "Shelby" in print(a);
    print(a);
};
##

##

function fib(n : number, n : number) : number => 2;
print(fib(6));
##

##
function fib(n : number, n : number) : nn + 1;
##

##
print("a" + 2);
##

##

let x = 2 in print(x + y);
##

##
print(sin(10));
##

##

function g() => f(x);
function f() => g(x);
print("Boom");
##

##
function g(x) => f(x);
function f(x) => g(x);
print("Semantic should work but code don't");
##

## 
print("The message is \"Hello World\"");
##

##

let a = 10 in { 
            a := "A";
            print(a);
            };
##

##

type Knight inherits Person {
    name() => "Sir" @@ base();
}

let p = new Knight("Phil", "Collins") in
    print(p.name());
##

##

let pt = new PolarPoint(3,4) in
    print("rho: " @ pt.rho());
##

##
function first_square(z : Number)
{
    let len = z, squares = [x^2 || x in range(1, len+1, 1)], st = 0, ed = len - 1, middle = 0 
        in {
            while(ed - st > 0)
            {
                middle := st + (ed - st)/2;
                if (squares[middle] >= z)
                {
                    ed := middle;
                }
                else
                {
                    st := middle + 1;
                };
            };
            if (ed - 1 >= st & squares[ed-1] >= z)
            {
                ed := ed - 1; 
            }
            else
            {
                ed := ed;
            };
            squares[ed];    
        };
};
print(first_square(10));
##

##
let squares = [x^2 || x in range(1,x)] in print(x);
##

##


let squares = [x^2 || x in range(1, 10)] in print(x + y);
##

##

let squares = [x^2 || x in range(1, 10)] in print(x + y);
##

##
type range(st:Number, ed:Number, offset : Number) {
    st = st;
    ed = ed;
    current = st - offset;

    next(): Boolean => (self.current := self.current + offset) < ed;
    current(): Number => self.current;
}


function parseTerm(tokens: Vector){
    let node = LiteralNode(tokens[0]), done = false in 
    {
        for( i in range(len(tokens)-1, -1, -1))
        {
            if (!done & (tokens[i] == "+" | tokens[i] == "-"))
            {
                let right = parseFactor(i+1, tokens),
                    op = tokens[i],
                    toks = [tokens[x] || x in range(0, i)], 
                    left = parseTerm(toks),
                    done = true in 
                {
                    node := BinaryNode(left, op, right);
                };
            }
            else
            {
                4;
            };
        };
    };
};

function parseFactor(cr : int, tokens : Vector){
    let node = LiteralNode(tokens[cr]) in {
        if (cr == len(tokens))
        {
            node;
        }
        else
        {
            let op = tokens[cr], right = parseFactor(cr + 1, tokens) in {
                BinaryNode(node, op, right);
            };
        };
    };
};

protocol Node {
    eval() : Number;
}

type LiteralNode(value : Number) {
    value = value;
    eval() => value;
}

type BinaryNode(left : Node, op : string, right : Node) {
    left = left;
    op = op;
    right = right;
    eval() {
        if(op == "+")
        {
            eval(left) + eval(right);
        }
        elif (op == "-")
        {
            eval(left) - eval(right);
        }
        elif (op == "*")
        {
            eval(left) * eval(right);
        }
        else
        {
            eval(left) / eval(right);
        };
    };
}
let node = parseTerm([3, "*", 2, "*", 4, "-", 1, "-", 1]) in print(node.eval());
##

##

print(sin(1.03432)^2 + cos(1.03432)^2);
##

##
4 @ 4;
##

##

type Person
{
    message = "Hi";
    greet() => print(self.message);
}

(new Person()).greet();
##

##

type Num
{
    num = 4;
    get_num() => self.num;
}
print(3^(new Num()).get_num())
##

##

type Num
{
    num = 4;
    get_num() => self.num;
}
print(3^(new Num()).get_num())
##

##

type Superman {
}
type Bird {
}
type Plane {
}
4;
##

##

type A {
    hello() => print("A");
}

type B inherits A {
    hello() => print("B");
}

type C inherits A {
    hello() => print("C");
}
4;
##

##

print(tan(PI) ** 2 + cot(PI) ** 2); #error
let msg = "Hello World" in print(msg);
let number = 42, text = "The meaning of life is" in
    print(text @ number);
let number = 42 in
    let text = "The meaning of life is" in
        print(text @ number);
let number = 42 in (
    let text = "The meaning of life is" in (
            print(text @ number);
        )
    );
let a = 6, b = a * 7 in print(b);
let a = 6 in
    let b = a * 7 in
        print(b);
let a = 5, b = 10, c = 20 in {
    print(a+b);
    print(b*c);
    print(c/a);
};
let a = (let b = 6 in b * 7) in print(a);
print(let b = 6 in b * 7);
let a = 20 in {
    let a = 42 in print(a);
    print(a);
};
let a = 7, a = 7 * 6 in print(a);
let a = 7 in
    let a = 7 * 6 in
        print(a);
let a = 0 in {
    print(a);
    a := 1;
    print(a);
};
let a = 0 in
    let b = a := 1 in {
        print(a);
        print(b);
    };
let a = 42 in if (a % 2 == 0) print("Even") else print("odd");
let a = 42 in print(if (a % 2 == 0) "even" else "odd");
let a = 42 in
    if (a % 2 == 0) {
        print(a);
        print("Even");
    }
    else print("Odd");
let a = 42, mod = a % 3 in # error
    print(
        if (mod == 0) "Magic"
        elif (mod % 3 == 1) "Woke"
        else "Dumb"
    );
let a = 10 in while (a >= 0) {
    print(a);
    a := a - 1;
}
##

##

{ 
    print("The message is \\\" Hello World \\\" " @ "and\\\"nothing else \\\"");
};
##

##

{ 
    let p = new Knight("Phil", "Collins") in print(p.name());
};
##

## 

type Node(value : number)
{
    value = value;
    previous = self;
    next = self;
    addPrevious(previous : Node) : Node => self.previous := previous;
    addNext(next : Node) : Node => self.next := next;
    getPrevious() : Node => self.previous;
    getNext() : Node => self.next;
    print() : number => print(self.value);
}

let n1 = new Node(4), n2 = new Node(6), n3 = new Node(8) in 
{
    n1.addNext(n2);
    n2.addNext(n3);
    n2.addPrevious(n1);
    n3.addPrevious(n2);
    n1.getNext().getNext().print();
    n2.getPrevious().print();
};
##

##
{
    print("\\\" a"); 
}
##

## 
{
	print("Alvaro says: 'what is a regular expression'");
    print("Someone older says to him: \\\"let drama go\\\"");
    print("He answers with \\\"Speak is easy\\\"");
    print("There is no need to escape this ' symbol because in Hulk it is not a special character");
}
## 

##
type range(st:Number, ed:Number, offset : Number) {
    st = st;
    ed = ed;
    offset = offset;
    current = st - offset;

    next(): Boolean => (self.current := self.current + self.offset) < self.ed;
    m(): Number => self.current;
}

let X = new range(3, 6, 1) in while(X.next())
{
    print(X.m());
};
##