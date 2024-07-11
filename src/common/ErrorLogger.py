from termcolor import colored

class Error:
    def __init__(self, message : str, line : int, offset : int):
        self.message = message
        self.line = line
        self.offset = offset

    def show(self, inputStr):
        line =  self.line
        position = self.offset
        lines = inputStr.split("\n")
        error_line = lines[line]
        print(colored(f"Error on line {line}, " + "message : " + self.message, "red"))
        print(error_line)
        print(" " * (position) + "^")