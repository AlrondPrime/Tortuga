import os.path

import win32gui
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThreadPool, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidgetItem, QMenu, QStyle, QApplication
from PyQt5.QtWinExtras import QtWin

from App import App
from AppEditForm import AppEditForm
from ThreadLaunch import ThreadLaunch


class _ListWidgetItemSignals(QObject):
    gameClosed = pyqtSignal()
    errorLaunching = pyqtSignal(int)
    updateTime = pyqtSignal(object)


class ListWidgetItem(QListWidgetItem):
    def __init__(self):
        super(ListWidgetItem, self).__init__()
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.signals = _ListWidgetItemSignals()
        self._launcher = None
        self._app = App()
        self._timer = QTimer()
        self._timer.setInterval(60_000)  # 1 minute

        self._edit_form = AppEditForm()

        self._timer.timeout.connect(self._increaseTime)
        self._edit_form.signals.dataEdited.connect(self._updateData)

        self.context_menu = QMenu()
        self.context_menu.addAction("Edit", self._showEditForm)
        self.setTextAlignment(Qt.AlignCenter)

    def toJSON(self):
        return self._app.toJSON()

    def fromJSON(self, app_json: dict):
        self._app.fromJSON(app_json)

    def setTitle(self, title: str):
        self._app.title = title

    def totalTime(self):
        return self._app.hours, self._app.minutes

    def currentTime(self):
        return self._app.current_hours, self._app.current_minutes

    def _increaseTime(self) -> None:
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

    def setApp(self, app: App):
        self._app = app
        self.setText(self._app.title)
        self._updateIcon()

    def launchGame(self) -> None:
        # self.setBackground(QColor(Qt.green))
        self._app.current_hours = 0
        self._app.current_minutes = 0
        self._launcher = ThreadLaunch(self._app)
        QThreadPool.globalInstance().start(self._launcher)
        self._launcher.signals.gameClosed.connect(self.gameClosed)
        self._launcher.signals.error.connect(self.errorLaunching)

        self._timer.start()
        self.signals.updateTime.emit(self)

    def gameClosed(self) -> None:
        # self.setBackground(QColor(Qt.white))
        self._timer.stop()

        self.signals.gameClosed.emit()

    def errorLaunching(self, code: int) -> None:
        self.signals.errorLaunching.emit(code)

    def _updateData(self, app_json: dict) -> None:
        self._edit_form.title_field.clear()
        self._edit_form.path_field.clear()

        title = app_json['title']
        path = app_json['path']

        if title != "":
            self._app.title = title
            self.setText(title)

        if path != "":
            self._app.path = path

        self._updateIcon()

    def _showEditForm(self) -> None:
        self._edit_form.title_field.setText(self._app.title)
        self._edit_form.path_field.setText(self._app.path)
        self._edit_form.show()

    # override
    def _updateIcon(self):
        if os.path.exists(self._app.path):
            icons = win32gui.ExtractIconEx(self._app.path, 0, 10)
            if len(icons[0]) != 0:
                if len(icons[0]) >= 1:
                    pixmap = QtWin.fromHICON(icons[0][0])
                    icon = QIcon(pixmap)
                    win32gui.DestroyIcon(icons[0][0])
                    win32gui.DestroyIcon(icons[1][0])
                    super().setIcon(icon)
            else:
                super().setIcon(QIcon("./resources/Default.ico"))
        else:
            super().setIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical))

    def exists(self) -> bool:
        return os.path.exists(self._app.path)
