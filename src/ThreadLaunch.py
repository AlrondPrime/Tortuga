import os
import time
from re import search

import psutil
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal


class LauncherSignals(QObject):
    done = pyqtSignal(str)
    error = pyqtSignal(int)


class ThreadLaunch(QRunnable):
    def __init__(self, app):
        super(QRunnable, self).__init__()
        self.app = app
        self.signals = LauncherSignals()

    def run(self):
        # now = time.time()
        if os.path.exists(self.app.path):
            result = search(r'(?P<name>.+)/.+.exe', self.app.path)

            if not result:
                print("Error with path")
                self.signals.error.emit(-1)
                return

            proc = psutil.Popen([], executable=self.app.path, cwd=result.group('name'))
            name = proc.name()
            proc.wait()
            for proc2 in psutil.process_iter():
                if proc2.name() == name:
                    proc2.wait()
        # now2 = time.time()
        # session_time = int(now2 - now)
        # hours = self.app.hours
        # minutes = self.app.minutes
        # minutes += session_time // 60
        # if minutes >= 60:
        #     hours += minutes // 60
        #     minutes %= 60

        # self.app.hours = hours
        # self.app.minutes = minutes
        self.signals.done.emit(self.app.title)
