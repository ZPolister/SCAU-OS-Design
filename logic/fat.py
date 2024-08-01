from logic_constant import *
import system_io

FAT_SIZE = BLOCK_SIZE * 2  # FAT 占用两个块，共 128 字节


class fat:
    """
    构造函数，将磁盘的文件分配表读进来
    """

    def __init__(self) -> None:
        # 读0号和1号磁盘块作为FAT分区
        self._fat_buffer = system_io.read_block(0) + system_io.read_block(1)
        self._fat_buffer = [x for x in self._fat_buffer]
        self._fat_buffer[0] = self._fat_buffer[1] = self._fat_buffer[2] = FAT_EOF
        pass

    def _write_fat(self):
        system_io.write_block(FAT_START_BLOCK, bytes(self._fat_buffer[:BLOCK_SIZE]))
        system_io.write_block(FAT_END_BLOCK, bytes(self._fat_buffer[BLOCK_SIZE:]))

    def _find_free_blocks(self, count) -> list:
        free_blocks = []
        for i in range(len(self._fat_buffer)):
            if self._fat_buffer[i] == FAT_NULL:
                free_blocks.append(i)
                if len(free_blocks) == count:
                    break
        return free_blocks if len(free_blocks) == count else None

    def allocate_blocks(self, count) -> list | None:
        free_blocks = self._find_free_blocks(count)
        if not free_blocks:
            return None
        for i in range(count - 1):
            self._fat_buffer[free_blocks[i]] = free_blocks[i + 1]
        self._fat_buffer[free_blocks[-1]] = FAT_EOF
        self._write_fat()
        return free_blocks

    def free_blocks(self, start_block):
        current = start_block
        while current != FAT_EOF:
            next_block = self._fat_buffer[current]
            self._fat_buffer[current] = FAT_NULL
            current = next_block

        self._write_fat()


if __name__ == '__main__':
    pass
