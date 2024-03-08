import traceback
from multiprocessing import Pipe, Process


class CustomProcess(Process):

    def __init__(self, *args, **kwargs):
        self._parent_status_conn, self._child_status_conn = Pipe()
        if 'kwargs' not in kwargs:
            kwargs['kwargs'] = {}
        kwargs['kwargs']['conn'] = self._child_status_conn
        super().__init__(*args, **kwargs)
        self._parent_exception_conn, self._child_exception_conn = Pipe()
        self._is_started = False
        self._exception = None

    def run(self):
        try:
            Process.run(self)
        except Exception:
            self._child_exception_conn.send(traceback.format_exc())

    def is_started(self):
        if self._is_started:
            return True
        if self._parent_status_conn.poll():
            self._parent_status_conn.recv()
            self._parent_status_conn.close()
            self._is_started = True
            return True
        return False

    @property
    def exception(self):
        if self._parent_exception_conn.poll():
            self._exception = self._parent_exception_conn.recv()
        return self._exception

