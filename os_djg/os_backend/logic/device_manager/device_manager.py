from collections import deque

from os_backend.logic.device_manager.device import Device
from os_backend.logic.process_manager import pcb
from os_backend.logger import log


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
            log.info(f"所请求设备{device_name} 不存在。")
            return False

        # print(process.instructions)
        process_id = process.pid
        device = self.devices[device_name]
        request_info = {
            "process": process,
            "device": device_name,
            "time": device_time,
            "waiting_time": 0
        }
        if device.available_count > 0:
            device.available_count -= 1
            self.allocation_table[process_id] = request_info
            log.info(f"设备 {device_name} 分配给 {process_id}")
            return True
        else:
            log.info(f"设备 {device_name} 不足. 进程 {process_id} 进入等待队列")
            self.waiting_queue.append(request_info)
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

    def get_device_condition(self):

        return {
            'device_status': [
                {
                    'device_name': device.name,
                    'device_total_count': device.total_count,
                    'device_available_count': device.available_count
                }
                for device in self.devices.values()
            ],
            'allocation_status': [
                {
                    'process_id': process_id,
                    'device_name': process_info['device']
                }
                for process_id, process_info in self.allocation_table.items()
            ],
            'waiting_status': [
                {
                    'process_id': process['process'].pid,
                    'device_name': process['device'],
                    'waiting_time': process['waiting_time']
                }
                for process in self.waiting_queue
            ]
        }

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
        
        # 对还在等待的进程进行+1计数
        for process in self.waiting_queue:
            process['waiting_time'] += 1
            

    def print_status(self):
        log.info("设备状态：")
        for device in self.devices.values():
            log.info(f"设备{device.name}: {device.available_count}/{device.total_count} 可用")
        log.info("设备分配情况：")
        for process_id, device_name in self.allocation_table.items():
            log.info(f"进程 {process_id} -> 设备 {device_name}")
        log.info("Waiting Queue:")
        for process_id, device_name in self.waiting_queue:
            log.info(f"进程 {process_id} 正在等待 {device_name}")


# 单实例导出
deviceService = DeviceManager()
