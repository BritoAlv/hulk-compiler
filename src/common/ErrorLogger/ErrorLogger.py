class ErrorLogger:
    def __init__(self) -> None:
        self.errors = []
    def add(self, msg):
        self.errors.append(msg)
    def log_errors(self):
        for i in self.errors:
            print(i)