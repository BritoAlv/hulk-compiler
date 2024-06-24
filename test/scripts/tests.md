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