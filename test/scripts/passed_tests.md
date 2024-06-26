## 1
```hulk
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
```

## 2

```hulk
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
```