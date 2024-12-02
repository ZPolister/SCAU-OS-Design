import os.path
import threading

from django.apps import AppConfig

from os_backend.logic.process_manager import schedule
from os_backend.logic.process_manager.process_constant import RESULT_FILE_NAME


class OsBackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "os_backend"

    def ready(self):
        threading.Thread(target=schedule.system_timer, daemon=True).start()

        # 移除上次记录
        if os.path.exists(RESULT_FILE_NAME):
            os.remove(RESULT_FILE_NAME)

