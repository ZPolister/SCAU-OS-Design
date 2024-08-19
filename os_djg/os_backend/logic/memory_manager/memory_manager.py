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
                申请的内存块
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
                return allocated_block
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
        all_blocks = self.free_blocks + self.allocated_blocks
        all_blocks.sort(key=lambda x: x.start)
        merged_blocks = []
        current_block = None
        free_position_start = USER_MEMORY_SIZE + 1
        for block in all_blocks:
            if block.allocated:
                if block.start >= free_position_start:
                    block.start = free_position_start
                    free_position_start += block.size
                    # 更新进程块内内存地址
                    from os_backend.logic.process_manager.schedule import pcb_table
                    for pcb in pcb_table:
                        if pcb.pid == block.pid:
                            pcb.start_pos = block.start
                merged_blocks.append(block)
            else:
                if block.start < free_position_start:
                    free_position_start = block.start

        self.allocated_blocks = merged_blocks
        self.free_blocks = [MemoryBlock(free_position_start, USER_MEMORY_SIZE - free_position_start)]

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
    b1 = memoryService.allocate_memory(47)
    b2 = memoryService.allocate_memory(68)
    b3 = memoryService.allocate_memory(80)
    b4 = memoryService.allocate_memory(32)
    b5 = memoryService.allocate_memory(64)

    memoryService.print_memory()
    memoryService.free_memory(b2.start)
    memoryService.print_memory()
    memoryService.free_memory(b4.start)
    memoryService.print_memory()
