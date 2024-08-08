"""
    intro:
    全局常量
    
    usage:
    from disk_constant import *
"""

# 磁盘文件名
DISK_FILE_NAME = "disk"

# 磁盘块大小和数量
BLOCK_SIZE = 64
BLOCK_COUNT = 128

# 文件分配表起始和结束块
FAT_START_BLOCK = 0
FAT_END_BLOCK = 1

# FAT磁盘块尾标记
FAT_EOF = 0xFF

# FAT磁盘块空标记
FAT_NULL = 0x00

# 目录项大小
DIRECTORY_ENTRY_SIZE = 8

# 文件类型
ENTRY_FILE = 'e'
ENTRY_DIRECTORY = '\x00'

# 目录项偏移值
OFFSET_FILENAME = 3
OFFSET_EXTENSION = 4
OFFSET_ATTRIBUTES = 5
OFFSET_START_BLOCK = 6
OFFSET_LENGTH = 8
