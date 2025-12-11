import sys
import time
import threading
import itertools
from contextlib import contextmanager


class Spinner:
    """
    Minimal CLI spinner that:
      - animates on a background thread
      - prints to stderr (so stdout stays clean for data)
      - lets you update the current message
    """

    def __init__(
        self,
        message: str = "",
        frames=None,
        interval: float = 0.1,
    ):
        self.frames = frames or ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.interval = interval
        self._message = message
        self._stop = threading.Event()
        self._thread = None
        self._last_line_len = 0

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    def start(self):
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, final_message: str | None = None):
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join()
        self._thread = None
        # Clear the spinner line
        sys.stderr.write("\r" + " " * self._last_line_len + "\r")
        if final_message:
            sys.stderr.write(final_message + "\n")
        sys.stderr.flush()

    def _run(self):
        for frame in itertools.cycle(self.frames):
            if self._stop.is_set():
                break
            line = f"{frame} {self._message}"
            padded = line.ljust(self._last_line_len)
            self._last_line_len = max(self._last_line_len, len(line))
            sys.stderr.write("\r" + padded)
            sys.stderr.flush()
            time.sleep(self.interval)


@contextmanager
def spinning(message: str = "Working..."):
    """
    Convenience context manager:

    with spinning("Reading input...") as spin:
        ...
        spin.message = "Writing output..."
    """
    spin = Spinner(message=message)
    spin.start()
    try:
        yield spin
    finally:
        spin.stop()
