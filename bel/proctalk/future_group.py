class FutureGroup:
    def __init__(self, event_loop, log):
        self._event_loop = event_loop
        self._log = log
        self._futures = []

    def _cb_done(self, future):
        self._futures.remove(future)
        if not future.cancelled():
            exc = future.exception()
            if exc is not None:
                # TODO(nicholasbishop): handle in some way?
                self._log.error('future exception: %r', exc)

    def cancel_all(self):
        for future in self._futures:
            future.cancel()

    def create_task(self, coro):
        task = self._event_loop.create_task(coro)
        task.add_done_callback(self._cb_done)
        self._futures.append(task)
        return task
