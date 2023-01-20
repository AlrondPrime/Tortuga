from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThreadPool, pyqtSlot, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

from App import App
from ThreadLaunch import ThreadLaunch


class ListWidgetItemSignals(QObject):
    gameClosed = pyqtSignal(object)
    errorLaunching = pyqtSignal(int)
    updateTime = pyqtSignal(object)


class ListWidgetItem(QListWidgetItem):
    def __init__(self, text: str = "", parent: "ListWidget" = None):
        super(ListWidgetItem, self).__init__(text, parent)
        self._parent = parent
        self._app = App()
        self.signals = ListWidgetItemSignals()
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.timer = QTimer()
        self.timer.setInterval(60000)
        self.timer.timeout.connect(self.increaseTime)

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

    def totalTime(self):
        return self._app.hours, self._app.minutes

    def currentTime(self):
        return self._app.current_hours, self._app.current_minutes

    def increaseTime(self):
        self._app.current_minutes += 1
        if self._app.current_minutes == 60:
            self._app.current_minutes = 0
            self._app.current_hours += 1

        self._app.minutes += 1
        if self._app.minutes == 60:
            self._app.minutes = 0
            self._app.hours += 1

        if self.isSelected():
            self._parent.updateTime(self)

    def getApp(self):
        return self._app

    def setApp(self, app: App):
        self._app = app

    def launchGame(self):
        self.setBackground(QColor(Qt.green))
        self.timer.start()
        launcher = ThreadLaunch(self._app)
        QThreadPool.globalInstance().start(launcher)
        launcher.signals.done.connect(self.gameClosed)
        launcher.signals.error.connect(self.errorLaunching)

    def gameClosed(self, title: str):
        self.timer.stop()
        self.signals.gameClosed.emit(title)

    def errorLaunching(self, code: int):
        self.signals.errorLaunching.emit(code)
