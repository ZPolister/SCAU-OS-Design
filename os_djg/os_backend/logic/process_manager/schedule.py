# 全局寄存器和变量
import threading
import time

from os_backend.logic.process_manager.process_constant import *
from os_backend.logic.process_manager.pcb import PCB

IR = ""  # 指令寄存器
PSW = 0  # 程序状态字
PC = 0  # 程序计数器
x = 0  # 模拟寄存器
system_clock = 0  # 系统时钟
relative_clock = TIME_SLICE  # 相对时钟

pcb_table = []  # 进程控制块表
ready_queue = []  # 就绪队列
blocked_queue = []  # 阻塞队列
idle_process = PCB(0, [], '')  # 闲逛进程
running_process = idle_process  # 当前运行的进程


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


def create(instructions: list[str], path: str):
    """
    创建一个进程
    Args:
        path: 源文件路径
        instructions: 进程指令集
    Returns:

    """
    pid = len(pcb_table) + 1
    new_pcb = PCB(pid, instructions, path)
    pcb_table.append(new_pcb)
    ready_queue.append(new_pcb)
    print(f"Process {pid} created: {instructions}")


def destroy():
    """
    销毁进程，用于执行结束后的销毁
    Returns:

    """
    global running_process

    if running_process is not None:
        print(f"Process {running_process.pid} finished with x = {x}")
        pcb_table.remove(running_process)
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
            print(f"Process {process.pid} awakened.")


def CPU():
    global PC, IR, PSW, x, relative_clock

    if running_process and running_process.instructions:
        IR = running_process.instructions[PC]
        print(f'{system_clock}: {running_process.pid}-{IR}')
        # 解释执行指令
        if IR.startswith('x='):
            x = int(IR.split('=')[1])
        elif IR == 'x++':
            x += 1
        elif IR == 'x--':
            x -= 1
        elif IR.startswith('!'):
            PSW = PROCESS_IO
            PC += 1
            handle_interrupt()
            return
        elif IR == 'end':
            PSW = PROCESS_END

        PC += 1
        relative_clock -= 1

        # 时间片到点
        if relative_clock <= 0:
            PSW = PROCESS_TIMEOUT  # 设置时间片中断

        # 检查中断
        if PSW != 0:
            handle_interrupt()
    else:
        print(f'{system_clock}: {running_process.pid}-No Process Running')
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

        # 更新阻塞队列中的进程时间
        from os_backend.logic.device_manager.device_manager import deviceService
        deviceService.schedule_device()

        awake()


if '__main__' == __name__:
    create(['x=1', 'x++', '!A5', 'x--', 'end'], '')
    create(['x=1', 'x=7', '!A5', 'x--', 'end'], '')
    create(['x=1', 'x++', 'x=4', 'x--', 'x=9', '!B3', 'x--', 'end'], '')
    create(['x=2', 'x++', 'x++', 'end'], '')

    # 启动系统时钟
    threading.Thread(target=system_timer).start()
