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