from multiprocessing import Process

from django.apps import AppConfig
from django.conf import settings

from .server import ProxyServer


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    proxy_process = None

    def ready(self):
        host = settings.PROXY_SERVER_HOST
        port = settings.PROXY_SERVER_PORT
        server = ProxyServer(host, port)

        if self.proxy_process is None:
            self.proxy_process = Process(
                target=server.run,
                name="AiohttpServer",
                daemon=True
            )
            self.proxy_process.start()
