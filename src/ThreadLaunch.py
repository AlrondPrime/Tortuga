import os
from re import search

import psutil
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal


class LauncherSignals(QObject):
    gameClosed = pyqtSignal()
    error = pyqtSignal(int)


class ThreadLaunch(QRunnable):
    def __init__(self, app):
        super(QRunnable, self).__init__()
        self.app = app
        self.signals = LauncherSignals()

    def run(self):
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

        self.signals.gameClosed.emit()
