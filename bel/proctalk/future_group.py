class FutureGroup:
    def __init__(self, event_loop):
        self._event_loop = event_loop
        self._futures = []

    def _cb_done(self, future):
        self._futures.remove(future)
        if not future.cancelled():
            exc = future.exception()
            if exc is not None:
                # TODO(nicholasbishop): handle in some way?
                logging.error('listen exception: %s', exc)

    def cancel_all(self):
        for future in self._futures:
            future.cancel()

    def create_task(self, coro):
        task = self._event_loop.create_task(coro)
        task.add_done_callback(self._cb_done)
        self._futures.append(task)
        return task
