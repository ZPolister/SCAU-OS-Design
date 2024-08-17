from os_backend.logic.process_manager.process_constant import READY


class PCB:
    def __init__(self, pid, instructions, path, start_pos):
        self.pid = pid
        self.instructions = instructions
        self.state = READY
        self.pc = 0
        self.x = 0
        self.waiting_for = None
        self.path = path
        self.start_pos = start_pos

    def to_dict(self) -> dict:
        return {
            'pid': self.pid,
            'instructions': self.instructions,
            'state': self.state,
            'pc': self.pc,
            'x': self.x,
            'waiting_for': self.waiting_for,
            'path': self.path,
            'start_pos': self.start_pos,
        }
