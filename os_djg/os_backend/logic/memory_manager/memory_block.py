class MemoryBlock:
    """
    Memory Block 内存块
    """
    def __init__(self, start: int, size: int, allocated=False):
        self.start = start
        self.size = size
        self.allocated = allocated
