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