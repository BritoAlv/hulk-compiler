## 1
```hulk
function factorial(n : number) : number => 
if (n < 1)
    1
else
    n * factorial(n - 1);

print(factorial(5));
```

## 2
```hulk
function fibonacci(n : number) : number => 
if (n < 2)
    1
else
    fibonacci(n - 1) + fibonacci(n - 2);

print(fibonacci(5));
```

## 3
```hulk
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
```

## 4
```hulk
function fib(n : number) : number => if (n == 0 | n == 1) 1 else fib(n-1) + fib(n-2);

print(fib(6));
```

## 5
```hulk
function fib(n : number, n : number) : number => 2;
print(fib(6));
```

## 6
```hulk
function fib(n : number, n : number) : nn + 1;
```

## 7
```hulk
print(print(2));
```

## 8
```hulk
print("a" + 2);
```

## 9
```hulk
let x = 2 in print(x + y);
```

## 10
```hulk
type Knight inherits Person {
    name() => "Sir" @@ base();
}
type Person(firstname, lastname) {
    firstname = firstname;
    lastname = lastname;
    ada = 43;
    name() => self.firstname @@ self.lastname;
    hash() : Number {
        5;
    }
}
```

## 11
```hulk
print(sin(10));
```

## 12
```hulk
function g() => f(x);
function f() => g(x);
print("Boom");
```

## 13
```hulk
function g(x) => f(x);
function f(x) => g(x);
print("Semantic should work but code don't");
```

## 14
```hulk
print("The message is \"Hello World\"");
```

## 15
```hulk
let a = 10 in { 
            a := "A";
            print(a);
            };
```

## 16
```hulk
type Knight inherits Person {
    name() => "Sir" @@ base();
}

let p = new Knight("Phil", "Collins") in
    print(p.name());
```

## 17
```hulk
let pt = new PolarPoint(3,4) in
    print("rho: " @ pt.rho());
```
## 18
```hulk
# print first square greater or equal than x.
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
```

## 19
```hulk
# semantic error
let squares = [x^2 || x in range(1,x)] in print(x);
```

## 20
```hulk
# semantic error
let squares = [x^2 || x in range(1, 10)] in print(x + y);
```

## 21
```hulk
# semantic error
let squares = [x^2 || x in range(1, 10)] in print(x + y);
```
## 22
```hulk
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
```

## 23
```hulk
print(sin(1.03432)^2 + cos(1.03432)^2);
```

## 24
```hulk
4 @ 4;
```

## 25
```hulk
type Person
{
    message = "Hi";
    greet() => print(self.message);
}

(new Person()).greet();
```
## 26
```hulk

type Num
{
    num = 4;
    get_num() => self.num;
}
print(3^(new Num()).get_num())
```

## 27
```hulk
type Num
{
    num = 4;
    get_num() => self.num;
}
print(3^(new Num()).get_num())
```

## 28
```hulk
type Superman {
}
type Bird {
}
type Plane {
}
4;
```

## 29
```hulk
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
```