import os
from logic_constant import *
import system_io
import fat

# 根目录块大小
ROOT_DIR_BLOCK = 2


class disk:

    def __init__(self) -> None:
        # 读实机磁盘文件，判断有没有，若没有，则初始化写一个
        self._root_dir = None
        if not os.path.isfile(DISK_FILE_NAME):
            system_io.initialize_disk()
        # 初始化文件分配表
        self._fat = fat.fat()

        # 初始化根目录
        self._root_dir = system_io.read_block(ROOT_DIR_BLOCK)

    def create_file(self, path, ext, content):
        # 解析路径并找到父目录块
        parent_dir_block = find_parent_dir(path)
        if not parent_dir_block:
            print(f"Directory not found: {path}")
            return

        # 分配文件所需的磁盘块
        fat = read_fat()
        needed_blocks = (len(content) + BLOCK_SIZE - 1) // BLOCK_SIZE
        blocks = allocate_blocks(fat, needed_blocks)
        if not blocks:
            print("Not enough space on disk")
            return

        # 创建目录项
        filename = os.path.basename(path)
        dir_entry = create_directory_entry(filename, ext, blocks[0], len(content))
        write_directory_entry(parent_dir_block, dir_entry)

        # 写入文件内容到磁盘块
        for i in range(needed_blocks):
            block_data = content[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE].ljust(
                BLOCK_SIZE, b"\x00"
            )
            write_block(blocks[i], block_data)

    def delete_file(path):
        # 解析路径并找到文件目录项
        dir_block, entry_offset = find_directory_entry(path)
        if dir_block is None:
            print(f"File not found: {path}")
            return

        # 读取目录项，获取文件起始块
        dir_entry = read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]

        # 释放文件占用的磁盘块
        fat = read_fat()
        free_blocks(fat, start_block)

        # 删除目录项
        delete_directory_entry(dir_block, entry_offset)

    # 显示文件内容
    def type_file(path):
        # 解析路径，找到文件目录项
        # 读取文件内容并显示
        pass

    # 拷贝文件
    def copy_file(src_path, dest_path):
        # 解析源文件和目标路径
        # 拷贝文件内容
        pass

    # 创建目录
    def mkdir(path):
        # 解析路径，找到父目录块
        # 创建目录项
        pass

    # 删除空目录
    def rmdir(path):
        # 解析路径，找到目录项
        # 检查目录是否为空，删除目录项
        pass

    # 运行可执行文件
    def run_executable(path):
        # 解析路径，找到可执行文件内容
        # 模拟执行文件命令
        pass

    # 用户命令接口
    def command_interface():
        while True:
            command = input("$ ")
            args = command.split()
            if args[0] == "create":
                create_file(args[1], args[2])
            elif args[0] == "delete":
                delete_file(args[1])
            elif args[0] == "type":
                type_file(args[1])
            elif args[0] == "copy":
                copy_file(args[1], args[2])
            elif args[0] == "mkdir":
                mkdir(args[1])
            elif args[0] == "rmdir":
                rmdir(args[1])
            elif args[0] == "run":
                run_executable(args[1])
            elif args[0] == "exit":
                break
            else:
                print("Unknown command")


if __name__ == "__main__":
    initialize_disk()
    initialize_fat_and_root()
    command_interface()
