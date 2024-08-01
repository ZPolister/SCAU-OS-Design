"""
    intro:
    全局常量
    
    usage:
    from logic_constant import *    
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


