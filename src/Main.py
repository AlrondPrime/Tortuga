import os
import sys

import psutil
from PyQt5.QtWidgets import QApplication

from MainWindow import MainWindow


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    # Check if this app is already launched
    instances_count = 0
    for proc in psutil.process_iter():
        if proc.name() == "Tortuga.exe" and proc.cwd() == os.getcwd() and proc.pid != os.getpid():
            instances_count += 1
        elif proc.name() == "pythonw.exe" and proc.cwd() == os.getcwd() and proc.pid != os.getpid():
            instances_count += 1

    if instances_count > 1:
        if sys.executable[-10:-4] == "python":  # running in IDE
            print("Found redundant Tortuga instances")
        else:
            sys.exit(0)

    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
