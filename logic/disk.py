import os
import struct
from logic_constant import *
import system_io
import fat

# 根目录块大小
ROOT_DIR_BLOCK = 2


class Disk:
    def __init__(self) -> None:
        # 读实机磁盘文件，判断有没有，若没有，则初始化写一个
        self._root_dir = None
        if not os.path.isfile(DISK_FILE_NAME):
            system_io.initialize_disk()
        # 初始化文件分配表
        self._fat = fat.FAT()

        # 初始化根目录
        self._root_dir = system_io.read_block(ROOT_DIR_BLOCK)

    def create_file(self, path, ext, content):
        # 解析路径并找到父目录块
        parent_dir_block, dir_name = self.find_parent_dir(path)
        if not parent_dir_block:
            print(f"Directory not found: {path}")
            return

        # 分配文件所需的磁盘块
        needed_blocks = (len(content) + BLOCK_SIZE - 1) // BLOCK_SIZE
        blocks = self._fat.allocate_blocks(needed_blocks)
        if not blocks:
            print("Not enough space on disk")
            return

        # 创建目录项
        filename = os.path.basename(path)
        dir_entry = self.create_directory_entry(filename, ext, blocks[0], len(content))
        self.write_directory_entry(parent_dir_block, dir_entry)

        # 写入文件内容到磁盘块
        for i in range(needed_blocks):
            block_data = content[i * BLOCK_SIZE: (i + 1) * BLOCK_SIZE].ljust(
                BLOCK_SIZE, b"\x00"
            )
            system_io.write_block(blocks[i], block_data)

    def delete_file(self, path):
        # 解析路径并找到文件目录项
        dir_block, entry_offset = self.find_directory_entry(path)
        if dir_block is None:
            print(f"File not found: {path}")
            return

        # 读取目录项，获取文件起始块
        dir_entry = self.read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]

        # 释放文件占用的磁盘块
        self._fat.free_blocks(start_block)

        # 删除目录项
        self.delete_directory_entry(dir_block, entry_offset)

    def find_parent_dir(self, path):
        # 解析路径，找到父目录块
        # 例如：path = \aa\bb\file.txt
        parts = path.strip("\\").split("\\")
        current_block = ROOT_DIR_BLOCK
        for part in parts[:-1]:  # 不包括最后一个部分，即文件名
            dir_entry = self.find_directory_entry_in_block(current_block, part)
            if not dir_entry:
                return None, part
            current_block = dir_entry["start_block"]
        return current_block, parts[-1]

    def find_directory_entry_in_block(self, block, name):
        block_data = system_io.read_block(block)
        for i in range(0, len(block_data), DIRECTORY_ENTRY_SIZE):
            entry = block_data[i:i + DIRECTORY_ENTRY_SIZE]
            if entry[:3].strip(b'\x00') == name.encode():
                return self.parse_directory_entry(entry)
        return None

    def parse_directory_entry(self, entry):
        filename = entry[:3].strip(b'\x00').decode()
        ext = entry[3:4].decode()
        attr = entry[4]
        start_block = entry[5]
        length = struct.unpack('<H', entry[6:8])[0]
        return {
            "filename": filename,
            "ext": ext,
            "attr": attr,
            "start_block": start_block,
            "length": length
        }

    def create_directory_entry(self, filename, ext, start_block, length):
        filename = filename.ljust(3, '\x00').encode()
        ext = ext.ljust(1, '\x00').encode()
        attr = 0  # 0 表示普通文件
        start_block = struct.pack('<B', start_block)
        length = struct.pack('<H', length)
        return filename + ext + bytes([attr]) + start_block + length

    def write_directory_entry(self, parent_dir_block, dir_entry):
        block_data = bytearray(system_io.read_block(parent_dir_block))
        for i in range(0, len(block_data), DIRECTORY_ENTRY_SIZE):
            if block_data[i:i + 3] == b'\x00\x00\x00':  # 找到一个空目录项
                block_data[i:i + DIRECTORY_ENTRY_SIZE] = dir_entry
                system_io.write_block(parent_dir_block, block_data)
                return
        # 如果当前块没有空位，需要分配新块（本示例简单处理，没有处理这种情况）
        print("No space in directory to add new file")

    def read_directory_entry(self, dir_block, entry_offset):
        block_data = system_io.read_block(dir_block)
        entry = block_data[entry_offset:entry_offset + DIRECTORY_ENTRY_SIZE]
        return self.parse_directory_entry(entry)

    def delete_directory_entry(self, dir_block, entry_offset):
        block_data = bytearray(system_io.read_block(dir_block))
        block_data[entry_offset:entry_offset + DIRECTORY_ENTRY_SIZE] = b'\x00' * DIRECTORY_ENTRY_SIZE
        system_io.write_block(dir_block, block_data)

    def type_file(self, path):
        # 解析路径并找到文件目录项
        dir_block, entry_offset = self.find_directory_entry(path)
        if dir_block is None:
            print(f"File not found: {path}")
            return
        dir_entry = self.read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]
        length = dir_entry["length"]

        # 读取文件内容并显示
        content = b''
        current_block = start_block
        while current_block != 0xFF:
            content += system_io.read_block(current_block)
            current_block = self._fat.fat[current_block]
        print(content[:length].decode())

    def copy_file(self, src_path, dest_path):
        # 解析源文件和目标路径
        dir_block, entry_offset = self.find_directory_entry(src_path)
        if dir_block is None:
            print(f"File not found: {src_path}")
            return
        dir_entry = self.read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]
        length = dir_entry["length"]

        # 读取源文件内容
        content = b''
        current_block = start_block
        while current_block != 0xFF:
            content += system_io.read_block(current_block)
            current_block = self._fat.fat[current_block]

        # 创建目标文件
        self.create_file(dest_path, dir_entry["ext"], content[:length])

    def mkdir(self, path):
        # 解析路径并找到父目录块
        parent_dir_block, dir_name = self.find_parent_dir(path)
        if not parent_dir_block:
            print(f"Directory not found: {path}")
            return

        # 分配目录所需的磁盘块
        blocks = self._fat.allocate_blocks(1)
        if not blocks:
            print("Not enough space on disk")
            return

        # 创建目录项
        dir_entry = self.create_directory_entry(dir_name, '', blocks[0], 0)
        self.write_directory_entry(parent_dir_block, dir_entry)

        # 初始化新目录块
        system_io.write_block(blocks[0], b'\x00' * BLOCK_SIZE)

    def rmdir(self, path):
        # 解析路径并找到目录项
        dir_block, entry_offset = self.find_directory_entry(path)
        if dir_block is None:
            print(f"Directory not found: {path}")
            return

        # 检查目录是否为空
        dir_entry = self.read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]
        block_data = system_io.read_block(start_block)
        if any(block_data[i:i + 3] != b'\x00\x00\x00' for i in range(0, BLOCK_SIZE, DIRECTORY_ENTRY_SIZE)):
            print(f"Directory not empty: {path}")
            return

        # 释放目录占用的磁盘块
        self._fat.free_blocks(start_block)

        # 删除目录项
        self.delete_directory_entry(dir_block, entry_offset)

    def run_executable(self, path):
        # 解析路径并找到可执行文件内容
        dir_block, entry_offset = self.find_directory_entry(path)
        if dir_block is None:
            print(f"File not found: {path}")
            return
        dir_entry = self.read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]
        length = dir_entry["length"]

        # 读取可执行文件内容
        content = b''
        current_block = start_block
        while current_block != 0xFF:
            content += system_io.read_block(current_block)
            current_block = self._fat.fat[current_block]
        content = content[:length].decode()

        # TODO 调用处理器部分实现运行
        return

    def list_directory(self, path):
        # 解析路径并找到目录块
        dir_block, _ = self.find_parent_dir(path)
        if dir_block is None:
            print(f"Directory not found: {path}")
            return

        # 读取目录块
        block_data = system_io.read_block(dir_block)

        # 逐行输出目录项
        for i in range(0, len(block_data), DIRECTORY_ENTRY_SIZE):
            entry = block_data[i:i + DIRECTORY_ENTRY_SIZE]
            if entry[:3] != b'\x00\x00\x00':  # 过滤空目录项
                dir_entry = self.parse_directory_entry(entry)
                print(f"{dir_entry['filename']}.{dir_entry['ext']}")

    def command_interface(self):
        while True:
            command = input("$ ")
            args = command.split()
            if not args:
                continue
            if args[0] == "create":
                self.create_file(args[1], 'e', args[2].encode())
            elif args[0] == "delete":
                self.delete_file(args[1])
            elif args[0] == "type":
                self.type_file(args[1])
            elif args[0] == "copy":
                self.copy_file(args[1], args[2])
            elif args[0] == "mkdir":
                self.mkdir(args[1])
            elif args[0] == "rmdir":
                self.rmdir(args[1])
            elif args[0] == "ls":
                self.list_directory(args[1] if len(args) > 1 else '\\')
            elif args[0] == "run":
                self.run_executable(args[1])
            elif args[0] == "exit":
                break
            else:
                print("Unknown command")


if __name__ == "__main__":
    disk = Disk()
    disk.command_interface()
