from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThreadPool, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem, QMenu

from App import App
from ThreadLaunch import ThreadLaunch
from AppEditForm import AppEditForm


class ListWidgetItemSignals(QObject):
    gameClosed = pyqtSignal()
    errorLaunching = pyqtSignal(int)
    updateTime = pyqtSignal(object)


class ListWidgetItem(QListWidgetItem):
    def __init__(self, text: str = ""):
        super(ListWidgetItem, self).__init__()
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.signals = ListWidgetItemSignals()
        self._launcher = None
        self.setText(text)
        self._app = App()
        self._timer = QTimer()
        self._timer.setInterval(60_000)  # 1 minute

        self.edit_form = AppEditForm()

        self._timer.timeout.connect(self.increaseTime)
        self.edit_form.dataEdited.connect(self.updateData)

        self.context_menu = QMenu()
        self.context_menu.addAction("Edit", self.showEditForm)

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
            self.signals.updateTime.emit(self)

    def getApp(self):
        return self._app

    def setApp(self, app: App):
        self._app = app

    def launchGame(self):
        self.setBackground(QColor(Qt.green))

        self._launcher = ThreadLaunch(self._app)
        QThreadPool.globalInstance().start(self._launcher)
        self._launcher.signals.gameClosed.connect(self.gameClosed)
        self._launcher.signals.error.connect(self.errorLaunching)

        self._timer.start()

    def gameClosed(self):
        self.setBackground(QColor(Qt.white))
        self._timer.stop()

        self.signals.gameClosed.emit()

    def errorLaunching(self, code: int):
        self.signals.errorLaunching.emit(code)

    def updateData(self, app_json: dict):
        self.edit_form.title_field.clear()
        self.edit_form.path_field.clear()

        title = app_json['title']
        path = app_json['path']

        if title != "":
            self._app.title = title
            self.setText(title)

        if path != "":
            self._app.path = path

    def showEditForm(self):
        self.edit_form.title_field.setPlaceholderText(self._app.title)
        self.edit_form.path_field.setPlaceholderText(self._app.path)
        self.edit_form.show()
