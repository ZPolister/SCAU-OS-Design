import logging

import os_backend.logic.disk_manager.disk_constant as logic_constant

"""_summary_
    对磁盘文件的IO，链接实机单文件
"""


# 初始化磁盘文件
def initialize_disk():
    with open(logic_constant.DISK_FILE_NAME, "wb") as f:
        f.write(b"\x00" * (logic_constant.BLOCK_SIZE * logic_constant.BLOCK_COUNT))


# 读取磁盘块
def read_block(block_number) -> bytes or None:

    if block_number >= logic_constant.BLOCK_COUNT:
        logging.warning("Block number %d is out of range", block_number)
        return None

    with open(logic_constant.DISK_FILE_NAME, "rb") as f:
        f.seek(block_number * logic_constant.BLOCK_SIZE)
        return f.read(logic_constant.BLOCK_SIZE)


# 写入磁盘块
def write_block(block_number, data) -> None:

    if len(data) != logic_constant.BLOCK_SIZE:
        logging.error('写入块大小错误')
        return

    with open(logic_constant.DISK_FILE_NAME, "r+b") as f:
        f.seek(block_number * logic_constant.BLOCK_SIZE)
        f.write(data)


if __name__ == "__main__":
    initialize_disk()
