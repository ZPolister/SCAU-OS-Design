import time
import threading
from datetime import datetime


class Logger:
    def __init__(self, log_to_file=False, file_name="log.txt", flush_interval=10):
        self.log_levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "RELEASE": 4}
        self.current_level = self.log_levels["DEBUG"]
        self.log_to_file = log_to_file
        self.file_name = file_name
        self.flush_interval = flush_interval
        self.buffer = []
        self.lock = threading.Lock()
        self.colors = {
            "DEBUG": "\033[0;37m",  # 白色
            "INFO": "\033[0;32m",  # 绿色
            "WARNING": "\033[0;33m",  # 黄色
            "ERROR": "\033[0;31m",  # 红色
            "RELEASE": "\033[0;36m",  # 青色
            "RESET": "\033[0m"  # 重置颜色
        }

        if self.log_to_file:
            self._start_background_flush()

    def _log(self, level, message):
        if self.log_levels[level] < self.current_level:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}][{level}] {message}"

        if self.log_to_file:
            with self.lock:
                self.buffer.append(log_message)
        else:
            # 控制台输出带颜色
            color = self.colors.get(level, self.colors["RESET"])
            print(f"{color}{log_message}{self.colors['RESET']}")

    def debug(self, message):
        self._log("DEBUG", message)

    def info(self, message):
        self._log("INFO", message)

    def warning(self, message):
        self._log("WARNING", message)

    def error(self, message):
        self._log("ERROR", message)

    def release(self, message):
        self._log("RELEASE", message)

    def set_level(self, level):
        if level.upper() in self.log_levels:
            self.current_level = self.log_levels[level.upper()]
        else:
            raise ValueError(f"Invalid log level: {level}")

    def _start_background_flush(self):
        def flush_buffer():
            while True:
                time.sleep(self.flush_interval)
                self._flush_to_file()

        flush_thread = threading.Thread(target=flush_buffer, daemon=True)
        flush_thread.start()

    def _flush_to_file(self):
        with self.lock:
            if self.buffer:
                with open(self.file_name, "a", encoding="utf-8") as f:
                    f.write("\n".join(self.buffer) + "\n")
                self.buffer.clear()

    def flush(self):
        self._flush_to_file()


log = Logger(log_to_file=False)
log.set_level("INFO")
