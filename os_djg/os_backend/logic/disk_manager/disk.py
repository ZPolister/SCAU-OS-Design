import logging
import os
import struct

from os_backend.logic.disk_manager.disk_constant import *
import os_backend.logic.disk_manager.system_io as system_io
import os_backend.logic.disk_manager.fat as fat
import os_backend.global_language.text as text

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

    def is_dir(self, entry) -> bool:
        return entry["ext"] == '\x00'

    def create_file(self, path, ext, content) -> str:
        """
        创建新的文件
        Args:
            path: 绝对路径
            ext: 拓展名
            content: 文件内容

        Returns:
            str: 执行信息
        """
        # 处理目录和文件名
        path = os.path.normpath(path)
        filename = path.split(os.sep)[-1]
        # 写死格式了，以后要改的时候再说吧
        if filename.endswith('.e'):
            filename = filename[:-2]

        # 解析路径并找到父目录块
        block, _, entry = self.find_directory_entry(path, ENTRY_FILE)
        if not block:
            return text.get_text('disk.dir_not_found') + f':{path}'

        if entry:
            return text.get_text('disk.file_already_exists') + f':{path}'

        # 分配文件所需的磁盘块
        needed_blocks = (len(content) // BLOCK_SIZE) + 1
        blocks = self._fat.allocate_blocks(needed_blocks)
        if not blocks:
            return text.get_text('disk.not_enough_space')

        # 创建目录项
        dir_entry = self.create_directory_entry(filename, ext, blocks[0], len(content))
        self.write_directory_entry(block, dir_entry)

        # 写入文件内容到磁盘块
        for i in range(needed_blocks):
            block_data = content[i * BLOCK_SIZE: (i + 1) * BLOCK_SIZE].ljust(
                BLOCK_SIZE, b"\x00"
            )
            system_io.write_block(blocks[i], block_data)

            return text.get_text('disk.file_created')

    def delete_file(self, path) -> bool:
        """
        删除文件
        Args:
            path: 待删除文件的路径

        Returns:
            是否删除成功
        """
        # 解析路径并找到文件目录项
        if not path.endswith('.e'):
            return False
        dir_block, entry_offset, dir_entry = self.find_directory_entry(path, ENTRY_FILE)
        if dir_block is None:
            print(f"File not found: {path}")
            return False

        if dir_entry is None or self.is_dir(dir_entry):
            print("could not delete directory")
            return False

        # 读取目录项，获取文件起始块
        dir_entry = self.read_directory_entry(dir_block, entry_offset)
        start_block = dir_entry["start_block"]

        # 释放文件占用的磁盘块
        self._fat.free_blocks(start_block)

        # 删除目录项
        self.delete_directory_entry(dir_block, entry_offset)
        return True

    def find_directory_entry(self, path, ext):
        """
        获得路径目录项所在的块以及偏移量
        Args:
            ext: 需要查找的为目录还是文件
            path: 路径参数

        Returns:
            第一个参数：所在磁盘块号
            第二个参数：目录项偏移量
            第三个参数：目录项信息
            如果为根目录目录项，第二个参数返回为 -1
        """
        path = os.path.normpath(path)
        # 解析路径并找到文件目录项
        parts = path.strip(os.sep).split(os.sep)

        # 根目录处理
        if path.strip(os.sep) == '':
            return ROOT_DIR_BLOCK, -1, None

        current_block = ROOT_DIR_BLOCK

        for part in parts[:-1]:
            _, dir_entry = self.find_directory_entry_in_block(current_block, part, ENTRY_DIRECTORY)
            if not dir_entry:
                return None, None, None
            current_block = dir_entry["start_block"]

        # 有文件尾缀的要去掉
        entry_name = parts[-1] if not parts[-1].endswith('.e') else parts[-1][:-2]

        entry = self.find_directory_entry_in_block(current_block, entry_name, ext)
        # 返回找到的文件目录项块号和目录项偏移量
        return current_block, entry[0], entry[1]

    def find_directory_entry_in_block(self, block, name, ext):
        """ docstrings
        通过目录项名查找目录项
        Args:
            ext: 查找文件类型（非必传）
            name: 待查找的文件名
            block: 磁盘块号

        Returns:
            参数1：目录项相对于磁盘块的偏移量
            参数2：待查找的文件信息，没有对应项则为空
        """
        block_data = system_io.read_block(block)
        for i in range(0, len(block_data), DIRECTORY_ENTRY_SIZE):
            entry = block_data[i:i + DIRECTORY_ENTRY_SIZE]
            entry = self.parse_directory_entry(entry)
            if (ext == ENTRY_FILE and not self.is_dir(entry)) \
                    or (ext == ENTRY_DIRECTORY and self.is_dir(entry)):
                if entry["filename"] == name:
                    return i, entry
        return None, None

    @staticmethod
    def parse_directory_entry(entry):
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
        """
        创建一个目录项
        """
        filename = filename.ljust(3, '\x00').encode()
        ext = ext.ljust(1, '\x00').encode()
        attr = 0  # 0 表示普通文件
        start_block = struct.pack('<B', start_block)
        length = struct.pack('<H', length)
        return filename + ext + bytes([attr]) + start_block + length

    def write_directory_entry(self, parent_dir_block, dir_entry):
        """
        在磁盘里写入目录项
        Args:
            parent_dir_block: 父目录磁盘号
            dir_entry: 待写入的目录项
        Returns:
            bool： 是否写入成功
        """
        previous_block = parent_dir_block
        while parent_dir_block != FAT_EOF:
            block_data = bytearray(system_io.read_block(parent_dir_block))
            for i in range(0, len(block_data), DIRECTORY_ENTRY_SIZE):
                if block_data[i:i + 3] == b'\x00\x00\x00':  # 找到一个空目录项
                    block_data[i:i + DIRECTORY_ENTRY_SIZE] = dir_entry
                    system_io.write_block(parent_dir_block, block_data)
                    return True

            # 根目录满了，不扩容，直接返回false
            if parent_dir_block == ROOT_DIR_BLOCK:
                return False

            previous_block = parent_dir_block
            parent_dir_block = self._fat.get_next_block(parent_dir_block)

        # 文件夹满了，申请扩容
        new_block = self._fat.allocate_blocks(1)
        if not new_block:
            return False

        self._fat.add_block(previous_block, new_block[0])
        system_io.write_block(new_block, dir_entry)
        return True

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
        dir_block, entry_offset, dir_entry = self.find_directory_entry(path, ENTRY_FILE)
        if dir_block is None or self.is_dir(dir_entry):
            print(f"File not found: {path}")
            return

        start_block = dir_entry["start_block"]
        length = dir_entry["length"]

        # 读取文件内容并显示
        content = b''
        current_block = start_block
        while current_block != 0xFF:
            content += system_io.read_block(current_block)
            current_block = self._fat.get_next_block(current_block)
        print(content[:length].decode())

    def copy_file(self, src_path: str, dest_path: str) -> str:
        """
        复制文件
        Args:
            src_path: 原文件路径
            dest_path: 目标路径

        Returns:
            执行信息
        """
        # 解析源文件和目标路径
        dir_block, entry_offset, dir_entry = self.find_directory_entry(src_path, ENTRY_FILE)
        if dir_entry is None:
            return text.get_text('disk.file_not_found')

        if self.is_dir(dir_entry):
            return text.get_text('disk.could_not_copy_directory')
        start_block = dir_entry["start_block"]
        length = dir_entry["length"]

        # 读取源文件内容
        content = b''
        current_block = start_block
        while current_block != 0xFF:
            content += system_io.read_block(current_block)
            current_block = self._fat.get_next_block(current_block)

        self.create_file(os.path.join(dest_path, dir_entry["filename"]), dir_entry["ext"], content[:length])
        return ''

    def mkdir(self, path):
        path = os.path.normpath(path)
        # 解析路径并找到父目录块
        parent_dir_block, _, entry = self.find_directory_entry(path, ENTRY_DIRECTORY)
        if not parent_dir_block:
            return text.get_text('disk.parent_directory_not_found')

        if entry:
            return text.get_text('disk.directory_already_exists')

        # 分配目录所需的磁盘块
        blocks = self._fat.allocate_blocks(1)
        if not blocks:
            return text.get_text('disk.no_enough_space')

        # 创建目录项
        dir_entry = self.create_directory_entry(path.split(os.sep)[-1], '', blocks[0], 0)
        self.write_directory_entry(parent_dir_block, dir_entry)

        # 初始化新目录块
        system_io.write_block(blocks[0], b'\x00' * BLOCK_SIZE)

    def rmdir(self, path):
        # 解析路径并找到目录项
        dir_block, entry_offset, _ = self.find_directory_entry(path, ENTRY_DIRECTORY)
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
        dir_block, entry_offset, entry = self.find_directory_entry(path, ENTRY_FILE)
        if dir_block is None:
            print(f"File not found: {path}")
            return
        if self.is_dir(entry):
            return "Can't execute directory."
        start_block = entry["start_block"]
        length = entry["length"]

        # 读取可执行文件内容
        content = b''
        current_block = start_block
        while current_block != 0xFF:
            content += system_io.read_block(current_block)
            current_block = self._fat.get_next_block(current_block)
        content = content[:length].decode()
        content.replace('\n', ' ')
        content = content.split(' ')
        content = list(filter(None, content))

        # # 占用内存
        # from os_backend.logic.memory_manager.memory_manager import memoryService
        # start_position = memoryService.allocate_memory(sum(len(item) for item in content))
        # CPU执行
        from os_backend.logic.process_manager.schedule import create
        create(content, path)

        return

    def get_file_list(self, path: str) -> list or None:
        """
        获得路径下目录列表
        Args:
            path: 绝对路径

        Returns:
            [
                {
                    filename: str
                    ext: str
                    start_block: int
                    length: int
                    content: bytes
                },
                ...,
            ]
        """
        # 解析路径并找到目录块
        _, flag, entry = self.find_directory_entry(path, ENTRY_DIRECTORY)
        if flag is None:
            logging.info("Directory not found: %s", path)
            return None
        dir_block = entry["start_block"] if flag != -1 else ROOT_DIR_BLOCK

        # 读取目录块
        block_data = b''
        while dir_block != 0xFF:
            block_data += system_io.read_block(dir_block)
            dir_block = self._fat.get_next_block(dir_block)

        # 逐行输出目录项
        result = []
        for i in range(0, len(block_data), DIRECTORY_ENTRY_SIZE):
            entry = block_data[i:i + DIRECTORY_ENTRY_SIZE]

            if entry[:3] != b'\x00\x00\x00':  # 过滤空目录项
                dir_entry = self.parse_directory_entry(entry)
                result.append(dir_entry)

        return result

    def list_directory(self, path) -> list or None:
        # 解析路径并找到目录块
        entry_list = self.get_file_list(path)
        if entry_list is None:
            return None

        return [f"{entry['filename']}{'.' + entry['ext'] if not self.is_dir(entry) else ''}" for entry in entry_list]

    def delete_directory(self, path) -> bool:
        """
        删除目录（可以删除非空文件夹）
        Args:
            path: 要删除目录的绝对路径
        Returns:

        """
        path = os.path.normpath(path)
        entry_list = self.get_file_list(path)
        if entry_list is None:
            return False

        for entry in entry_list:
            if path != os.sep:
                dir_path = os.path.join(path, entry["filename"] + ('' if self.is_dir(entry) else '.' + entry["ext"]))
            else:
                dir_path = os.sep + entry["filename"] + ('' if self.is_dir(entry) else '.' + entry["ext"])
            if not (self.delete_directory(dir_path) if self.is_dir(entry) else self.delete_file(dir_path)):
                return False
            else:
                print(f"deleted: {dir_path}")

        if path != os.sep:
            self.rmdir(path)
        return True

    def command_interface(self):
        while True:
            command = input("$ ")
            args = command.split()
            if not args:
                continue
            if args[0] == "create":
                msg = self.create_file(args[1], 'e', args[2].encode())
                print(msg)
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
                print(self.list_directory(args[1] if len(args) > 1 else '\\'))
            elif args[0] == "run":
                self.run_executable(args[1])
            elif args[0] == "deldir":
                self.delete_directory(args[1])
            elif args[0] == "exit":
                break
            else:
                print("Unknown command")


# 模块化单例
DiskService = Disk()

if __name__ == "__main__":
    disk = Disk()
    disk.command_interface()
    # disk.delete_directory('/')
