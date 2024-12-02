import threading
import time
import os
import csv

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from os_backend.logger import log
from os_backend.logic.process_manager.process_constant import *
from os_backend.logic.process_manager.pcb import PCB

# 全局寄存器和变量
IR = ""  # 指令寄存器
PSW = 0  # 程序状态字
PC = 0  # 程序计数器
x = 0  # 模拟寄存器
system_clock = 0  # 系统时钟
relative_clock = TIME_SLICE  # 相对时钟

pcb_table = []  # 进程控制块表
ready_queue = []  # 就绪队列
blocked_queue = []  # 阻塞队列
idle_process = PCB(0, [], '', -1)  # 闲逛进程
running_process = idle_process  # 当前运行的进程

# 总进程计数
process_id = 1


def schedule():
    """
    进程调度，保存现场，将当前就绪进程移动到前台运行
    Returns:

    """
    global running_process, PC, x, relative_clock

    if running_process and running_process != idle_process:
        running_process.pc = PC
        running_process.x = x
        running_process.state = READY
        ready_queue.append(running_process)

    if ready_queue:
        running_process = ready_queue.pop(0)
        PC = running_process.pc
        x = running_process.x
        running_process.state = RUNNING
        relative_clock = 5
    else:
        running_process = idle_process


def create(instructions: list[str], path: str) -> int | None:
    """
    创建一个进程
    Args:
        path: 源文件路径
        instructions: 进程指令集
    Returns:

    """

    global running_process, PC, x, relative_clock, process_id

    # 申请内存，内存不足时无法运行
    from os_backend.logic.memory_manager.memory_manager import memoryService
    allocated_block = memoryService.allocate_memory(sum(len(item) for item in instructions))
    if allocated_block is None:
        return None

    pid = process_id
    allocated_block.pid = pid
    new_pcb = PCB(pid, instructions, path, allocated_block.start)
    pcb_table.append(new_pcb)
    ready_queue.append(new_pcb)
    log.info(f"进程 {pid} 已创建: {path}")
    process_id += 1
    return pid


def destroy():
    """
    销毁进程，用于执行结束后的销毁
    Returns:

    """
    global running_process

    if running_process is not None:
        log.info(f"Process {running_process.pid} finished with x = {x}")
        write_result_to_csv(running_process)
        pcb_table.remove(running_process)
        # 释放占用的内存
        from os_backend.logic.memory_manager.memory_manager import memoryService
        memoryService.free_memory(running_process.start_pos)
        running_process = None
        schedule()


def block(reason):
    """
    阻塞当前进程
    Args:
        reason: 阻塞原因

    Returns:

    """
    global running_process, blocked_queue

    if running_process:
        running_process.state = BLOCKED
        running_process.waiting_for = reason
        running_process.pc = PC
        running_process.x = x
        blocked_queue.append(running_process)
        running_process = None
        schedule()


def awake():
    """
    唤醒所有阻塞的进程，将其加入就绪队列
    Returns:

    """
    for process in blocked_queue:
        if process.waiting_for is None:
            process.state = READY
            ready_queue.append(process)
            blocked_queue.remove(process)
            log.info(f"Process {process.pid} awakened.")


def CPU():
    global PC, IR, PSW, x, relative_clock

    if running_process and running_process.instructions:
        IR = running_process.instructions[PC]
        log.debug(f'{system_clock}: {running_process.pid}-{IR}')
        # 解释执行指令
        if IR.startswith('x='):
            x = int(IR.split('=')[1])
        elif IR == 'x++':
            x += 1
        elif IR == 'x--':
            x -= 1
        elif IR.startswith('!'):
            PSW = PROCESS_IO
        elif IR == 'end':
            PSW = PROCESS_END
        else:
            from os_backend.global_language.text import get_text
            send_message({
                'type': 'error_message',
                'content': get_text('ir.error')
            })
            
            # 销毁程序
            PSW = PROCESS_END

        PC += 1
        relative_clock -= 1

        # 时间片到点
        if relative_clock <= 0 and PSW == 0:
            PSW = PROCESS_TIMEOUT  # 设置时间片中断

        # 检查中断
        if PSW != 0:
            handle_interrupt()
    else:
        IR = ''
        schedule()


def handle_interrupt():
    global PSW
    if PSW == PROCESS_TIMEOUT:
        schedule()
    elif PSW == PROCESS_IO:
        device_name = IR[1]
        time_required = int(IR[2])

        from os_backend.logic.device_manager.device_manager import deviceService
        deviceService.request_device(running_process, device_name, time_required)
        block(PROCESS_IO)
    elif PSW == PROCESS_END:
        destroy()
    PSW = 0
    schedule()


def system_timer():
    global system_clock, blocked_queue

    while True:
        CPU()
        time.sleep(1)
        system_clock += 1

        # 向前端发送消息
        send_message(get_message_info())

        # 更新阻塞队列中的进程时间
        from os_backend.logic.device_manager.device_manager import deviceService
        deviceService.schedule_device()

        awake()


def send_message(message_content: any):
    # 获取通道层
    channel_layer = get_channel_layer()

    # 向所有连接的客户端发送消息
    async_to_sync(channel_layer.group_send)(
        'system_timer_group',
        {
            'type': 'send_timer_message',
            'message': message_content,
        }
    )


def get_message_info():
    """
    返回样式预览：
       见目录下process_message_info.md文件
    """
    from os_backend.logic.device_manager.device_manager import deviceService
    from os_backend.logic.memory_manager.memory_manager import memoryService
    from os_backend.logic.disk_manager.disk import DiskService
    return {
        'message_type': 'process_info',  # 消息类型，通过这项辨别是进程信息
        'system_clock': system_clock,  # 系统时间
        'now_process_id': running_process.pid,  # 现在运行的进程ID
        'relative_clock': relative_clock,  # 时间片
        'now_value': x,  # 现在寄存器的值
        'now_ir': IR,  # 现在执行的指令
        'ready_queue': [process.pid for process in ready_queue],  # 就绪进程id
        'total_memory': memoryService.total_memory,  # 总内存
        'user_memory': memoryService.user_memory,  # 用户区内存总数
        'user_memory_condition': memoryService.get_memory_condition(),  # 用户区内存使用情况
        'disk_usage': DiskService.get_disk_usage(),  # 磁盘块使用情况（记录使用的块号）
        'device_condition': deviceService.get_device_condition()  # 设备情况
    }


def write_result_to_csv(pcb: PCB) -> None:
    """
    写程序结果到CSV文件
    Args:
        pcb: 结束的进程
    Returns:
        None
    """
    result_row = [pcb.pid, pcb.path, pcb.x]

    # 判断文件是否存在
    file_exists = os.path.exists(RESULT_FILE_NAME)

    with open(RESULT_FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writerow(['PID', 'Path', 'Result'])

        # 写入结果
        writer.writerow(result_row)


if '__main__' == __name__:
    # 启动系统时钟
    threading.Thread(target=system_timer).start()
    create(['x=1', 'x++', '!A5', 'x--', 'end'], '')
    create(['x=1', 'x=7', '!A5', 'x--', 'end'], '')
    time.sleep(3)
    create(['x=1', 'x++', 'x=4', 'x--', 'x=9', '!B3', 'x--', 'end'], '')
    create(['x=2', 'x++', 'x++', 'end'], '')
