from os_backend.logic.process_manager.process_constant import READY

class PCB:
    def __init__(self, pid, instructions, path):
        self.pid = pid
        self.instructions = instructions
        self.state = READY
        self.pc = 0
        self.x = 0
        self.waiting_for = None
        self.path = path


