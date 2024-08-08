import threading

from django.apps import AppConfig

from os_backend.logic.process_manager import schedule


class OsBackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "os_backend"

    def ready(self):
        if not hasattr(self, 'started'):
            threading.Thread(target=schedule.system_timer).start()
            self.started = True  # 避免重复启动