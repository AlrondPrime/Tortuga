import os
from re import search

import psutil
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal


class _LauncherSignals(QObject):
    gameClosed = pyqtSignal()
    error = pyqtSignal(int)


class ThreadLaunch(QRunnable):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.signals = _LauncherSignals()

    # override
    def run(self):
        if os.path.exists(self._app.path):
            result = search(r'(?P<name>.+)[\\/].+.exe', self._app.path)

            if not result:
                print("Error with path")
                self.signals.error.emit(-1)
                return

            proc = psutil.Popen([], executable=self._app.path, cwd=result.group('name'))
            name = proc.name()
            proc.wait()
            for proc2 in psutil.process_iter():
                if proc2.name() == name:
                    proc2.wait()

        self.signals.gameClosed.emit()
