from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction


class SystemTrayIcon(QSystemTrayIcon):
    showWindow = pyqtSignal()
    closeWindow = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("./resources/Shipwreck.ico"))

        self.menu = QMenu()
        self.menu.addAction("Open Tortuga", self.showWindow)
        self.menu.addAction("Close Tortuga", self.closeWindow)
        self.setContextMenu(self.menu)

        self.show()
