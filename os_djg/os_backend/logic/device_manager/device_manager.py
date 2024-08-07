from collections import deque

from os_backend.logic.device_manager.device import Device
from os_backend.logic.process_manager import pcb


class DeviceManager:
    def __init__(self):
        self.devices = {
            'A': Device('A', 1),
            'B': Device('B', 2),
            'C': Device('C', 2)
        }
        self.allocation_table = {}
        self.waiting_queue = deque()

    def request_device(self, process: pcb, device_name: str, device_time: int) -> bool:
        """
        请求设备
        Args:
            device_time: 进程所需使用设备时间
            process: 进程ID
            device_name: 请求的设备名称

        Returns:
            是否申请成功
        """
        if device_name not in self.devices:
            print(f"Device {device_name} does not exist.")
            return False

        print(process.instructions)
        process_id = process.pid
        device = self.devices[device_name]
        if device.available_count > 0:
            device.available_count -= 1
            self.allocation_table[process_id] = {
                "process": process,
                "device": device_name,
                "time": device_time
            }
            print(f"设备 {device_name} 分配给 {process_id}")
            return True
        else:
            print(f"设备 {device_name} 不足. 进程 {process_id} 进入等待队列")
            self.waiting_queue.append({
                "process": process,
                "device": device_name,
                "time": device_time
            })
            return False

    def release_device(self, process_id: int) -> bool:
        """
        释放设备
        Args:
            process_id: 进程id

        Returns:
            是否释放成功
        """
        if process_id not in self.allocation_table:
            return False

        info = self.allocation_table.pop(process_id)
        device_name = info['device']
        process = info['process']
        device = self.devices[device_name]
        device.available_count += 1
        # 设置阻塞为None
        process.waiting_for = None

        # 从等待队列中查找，如果有正在等待的进程，那么让他上来
        for i, info in enumerate(self.waiting_queue):
            waiting_device_name = info['device']
            waiting_process = info['process']

            if waiting_device_name == device_name and device.available_count > 0:
                device.available_count -= 1
                self.allocation_table[waiting_process.pid] = info
                self.waiting_queue.remove(info)
                break

        return True

    def schedule_device(self):
        release_list = []
        for info in self.allocation_table.values():
            process = info['process']
            info['time'] -= 1

            if info['time'] <= 0:
                release_list.append(process.pid)
                # self.release_device(process.pid)
            else:
                self.allocation_table[process.pid] = info

        for pid in release_list:
            self.release_device(pid)

    def print_status(self):
        print("设备状态：")
        for device in self.devices.values():
            print(f"设备{device.name}: {device.available_count}/{device.total_count} 可用")
        print("设备分配情况：")
        for process_id, device_name in self.allocation_table.items():
            print(f"进程 {process_id} -> 设备 {device_name}")
        print("Waiting Queue:")
        for process_id, device_name in self.waiting_queue:
            print(f"进程 {process_id} 正在等待 {device_name}")


# 单实例导出
deviceService = DeviceManager()
