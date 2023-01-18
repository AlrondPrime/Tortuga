from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThreadPool, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

from src.App import App
from src.ThreadLaunch import ThreadLaunch


class ListWidgetItemSignals(QObject):
    gameClosed = pyqtSignal(object)
    errorLaunching = pyqtSignal(int)


class ListWidgetItem(QListWidgetItem):
    def __init__(self, text: str = ""):
        super().__init__(text)
        self._app = App()
        self.signals = ListWidgetItemSignals()
        self.setFlags(self.flags() | Qt.ItemIsEditable)

    def toJSON(self):
        return self._app.toJSON()

    def fromJSON(self, app_json: dict):
        self._app.fromJSON(app_json)

    def getTitle(self):
        return self._app.title

    def setTitle(self, title: str):
        self._app.title = title

    def setPath(self, path: str):
        self._app.path = path

    def getTime(self):
        return self._app.hours, self._app.minutes

    # TODO find usage for this
    def increaseTime(self):
        self._app.minutes += 1
        if self._app.minutes == 60:
            self._app.minutes = 0
            self._app.hours += 1

    def getApp(self):
        return self._app

    def setApp(self, app: App):
        self._app = app

    def launchGame(self):
        self.setBackground(QColor(Qt.green))
        launcher = ThreadLaunch(self._app)
        QThreadPool.globalInstance().start(launcher)
        launcher.signals.done.connect(self.gameClosed)
        launcher.signals.error.connect(self.errorLaunching)

    def gameClosed(self, title: str):
        self.signals.gameClosed.emit(title)

    def errorLaunching(self, code: int):
        self.signals.errorLaunching.emit(code)
