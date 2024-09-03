class Device:
    def __init__(self, name, count):
        self.name: str = name
        self.total_count: int = count
        self.available_count: int = count
