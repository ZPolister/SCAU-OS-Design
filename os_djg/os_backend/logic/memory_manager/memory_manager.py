from os_backend.logic.memory_manager.memory_block import MemoryBlock

USER_MEMORY_SIZE = 512
SYSTEM_MEMORY_SIZE = 64


class MemoryManager:
    """
    内存管理部分
    """

    def __init__(self, user_memory=USER_MEMORY_SIZE, system_memory=SYSTEM_MEMORY_SIZE):
        self.total_memory = user_memory + system_memory
        self.system_memory = system_memory
        self.user_memory = user_memory
        self.memory = bytearray(self.user_memory)
        self.free_blocks = [MemoryBlock(0, self.user_memory)]
        self.allocated_blocks = []

    def allocate_memory(self, size: int):
        """
            申请内存
            Args:
                size: 需要分配内存的大小
            Returns:
                申请内存的开始位置，如果没有合适的位置则为None
        """

        for block in self.free_blocks:
            # TODO 这里我暂时用的是首次适配，可以试试最佳适配（有合并操作应该不用做也行）
            if block.size >= size:
                # 取出这块内存
                self.free_blocks.remove(block)
                # 分配内存块
                allocated_block = MemoryBlock(block.start, size, True)
                # 加到已分配的内存块中
                self.allocated_blocks.append(allocated_block)

                # 用完了还有剩余的块，要把剩的还回去
                if block.size > size:
                    remaining_block = MemoryBlock(block.start + size, block.size - size)
                    self.free_blocks.append(remaining_block)
                self.free_blocks.sort(key=lambda x: x.start)
                return allocated_block.start
        return None

    def free_memory(self, start: int) -> bool:
        """
        释放内存
        Args:
            start: 释放内存块的开始位置
        Returns:
            释放是否成功
        """
        for block in self.allocated_blocks:
            if block.start == start:
                self.allocated_blocks.remove(block)
                block.allocated = False
                self.free_blocks.append(block)
                self.merge_free_blocks()
                return True
        return False

    def merge_free_blocks(self):
        """
        合并空闲内存块
        Returns:
            None
        """
        self.free_blocks.sort(key=lambda x: x.start)
        merged_blocks = []
        current_block = None
        for block in self.free_blocks:
            if current_block is None:
                current_block = block
            else:
                if current_block.start + current_block.size == block.start:
                    current_block.size += block.size
                else:
                    merged_blocks.append(current_block)
                    current_block = block
        if current_block is not None:
            merged_blocks.append(current_block)
        self.free_blocks = merged_blocks

    def print_memory(self):
        """
        打印内存空间，测试用
        """
        print("Free Blocks:")
        for block in self.free_blocks:
            print(f"{block.start}, {block.size}")

        print("Allocated Blocks:")
        for block in self.allocated_blocks:
            print(f" {block.start}, {block.size}")

    def get_memory_condition(self):
        memory_blocks = []
        for block in self.free_blocks:
            memory_blocks.append({
                "start": block.start,
                "size": block.size,
                "allocated": False
            })

        for block in self.allocated_blocks:
            memory_blocks.append({
                "start": block.start,
                "size": block.size,
                "allocated": True
            })

        return memory_blocks


memoryService = MemoryManager()

if __name__ == "__main__":
    pass
