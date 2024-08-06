from collections import deque
from os_backend.logic.device_manager.device import Device


class DeviceManager:
    def __init__(self):
        self.devices = {
            'A': Device('A', 1),
            'B': Device('B', 2),
            'C': Device('C', 2)
        }
        self.allocation_table = {}
        self.waiting_queue = deque()

    def request_device(self, process_id: str, device_name: str) -> bool:
        """
        请求设备
        Args:
            process_id: 进程ID
            device_name: 请求的设备名称

        Returns:
            是否申请成功
        """
        if device_name not in self.devices:
            print(f"Device {device_name} does not exist.")
            return False

        device = self.devices[device_name]
        if device.available_count > 0:
            device.available_count -= 1
            self.allocation_table[process_id] = device_name
            print(f"设备 {device_name} 分配给 {process_id}")
            return True
        else:
            print(f"设备 {device_name} 不足. 进程 {process_id} 进入等待队列")
            self.waiting_queue.append((process_id, device_name))
            return False

    def release_device(self, process_id: str) -> bool:
        """
        释放设备
        Args:
            process_id: 进程id

        Returns:
            是否释放成功
        """
        if process_id not in self.allocation_table:
            return False

        device_name = self.allocation_table.pop(process_id)
        device = self.devices[device_name]
        device.available_count += 1

        # 从等待队列中查找，如果有正在等待的进程，那么让他上来
        for i, (waiting_process_id, waiting_device_name) in enumerate(self.waiting_queue):
            if waiting_device_name == device_name and device.available_count > 0:
                device.available_count -= 1
                self.allocation_table[waiting_process_id] = waiting_device_name
                self.waiting_queue.remove((waiting_process_id, waiting_device_name))
                break

        return True

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
