import uuid
import asyncio
from threading import Thread


class ServerThread(object):
    def __init__(self, request_id):
        self.request_id = request_id
        self.stopped = False
        self.fixed_update_delay = 0.01

    def start(self):
        thread = Thread(target=self._run, args=())
        thread.start()

    def stop(self):
        self.stopped = True

    def _run(self):
        pass

    def _callback(self, callback):
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(callback())
