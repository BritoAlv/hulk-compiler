from ..common.token_class import Token

class ParseNode:
    def __init__(self, value: str) -> None:
        self.value: str = value
        self.parent: ParseNode = None  # type: ignore
        self.children: list[ParseNode] = []
        self.token: Token = None # type: ignore

    def print(self, ancestors_depth: list[int], depth: int, last_one: bool):
        branch = ''
        extending_branch = ''
        for i in range(0, depth):
            if i in ancestors_depth:
                branch += '|'
                extending_branch += '|'
            elif i < ancestors_depth[len(ancestors_depth) - 1]:
                branch += ' '
                extending_branch += ' '
            else:
                branch += '_'

        print(extending_branch)
        print(f'{branch}{self.value}')

        if last_one:
            ancestors_depth.pop()

        i = 0
        ancestors_depth.append(depth)
        for child in self.children:
            if i == len(self.children) - 1:
                child.print(list(ancestors_depth), depth + 8, True)
            else:
                child.print(list(ancestors_depth), depth + 8, False)
            i += 1