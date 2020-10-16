class Task:
    def __init__(self, request: str):
        self.request = request

    def __str__(self):
        return self.request

    def __repr__(self):
        return f'Task instance for "{self.request}"'
