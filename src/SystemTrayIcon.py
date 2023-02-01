from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu

from Helpers import Style


class _SystemTrayIconSignals(QObject):
    showWindow = pyqtSignal()
    exitApp = pyqtSignal()


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("./resources/Shipwreck.ico"))
        self.signals = _SystemTrayIconSignals()

        self.menu = QMenu()
        self.menu.setStyleSheet(Style("./styles/QMenu.qss"))
        self.menu.addAction("Open Tortuga", self.signals.showWindow)
        self.menu.addAction("Close Tortuga", self.signals.exitApp)
        self.setContextMenu(self.menu)

        self.show()

    def activateEvent(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == self.Trigger:  # Click
            self.signals.showWindow.emit()
