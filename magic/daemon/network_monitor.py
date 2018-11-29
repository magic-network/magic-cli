import threading
import time
from magic.util.log import log


class NetworkMonitor(threading.Thread):
    """ NetworkMonitor daemon

    Runs in the background and manages the connection to the Magic network.
    """

    def __init__(self, interval=1):
        """ Constructor

        :type interval: int
        :param interval: Check interval, in seconds
        """
        super(NetworkMonitor, self).__init__()

        self.interval = interval
        self.daemon = True
        self.paused = True
        self.state = threading.Condition()

    def run(self):
        self.resume()

        while True:
            with self.state:
                if self.paused:
                    # Block execution until notified.
                    self.state.wait()

            log("Checking for connection", "yellow")
            time.sleep(self.interval)

    def resume(self):
        with self.state:
            log("Resuming monitor", "green")
            self.paused = False
            self.state.notify()

    def pause(self):
        with self.state:
            log("Pausing monitor", "magenta")
            self.paused = True
