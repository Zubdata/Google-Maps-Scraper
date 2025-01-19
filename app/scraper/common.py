import threading

class Common:
    closeThread = threading.Event()
    lock = threading.Lock()

    @classmethod
    def set_close_thread(cls):
        with cls.lock:
            cls.closeThread.set()

    @classmethod
    def close_thread_is_set(cls):
        return cls.closeThread.is_set()
    