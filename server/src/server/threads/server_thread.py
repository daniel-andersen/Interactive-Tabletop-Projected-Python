import uuid
from threading import Thread


class ServerThread(object):
    def __init__(self):
        self.stopped = False
        self.id = uuid.uuid4()

    def start(self):
        thread = Thread(target=self._run, args=())
        thread.start()

    def stop(self):
        self.stopped = True

    def _run(self):
        pass
