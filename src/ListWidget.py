import json
import os.path
import shutil
from re import search

from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QContextMenuEvent
from PyQt5.QtWidgets import QListWidget, QFileDialog

from App import App
from Helpers import Style
from ListWidgetItem import ListWidgetItem


class _ListSignals(QObject):
    gameLaunched = pyqtSignal()
    gameClosed = pyqtSignal()
    updateTime = pyqtSignal(object)


def itemChange(item: ListWidgetItem):
    item.setTitle(item.text())


class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        self._path = R"./data/Tortuga.json"
        self._backup_path = R"./data/Tortuga-backup.json"
        self.setStyleSheet(Style("./styles/ListWidget.qss"))
        self.signals = _ListSignals()

        self.itemActivated.connect(self.launchGame)
        self.itemChanged.connect(itemChange)
        self.setDragDropMode(QListWidget.InternalMove)

        for app_json in self.load():
            app = App(app_json)
            item = ListWidgetItem(self)
            item.setApp(app)
            item.signals.updateTime.connect(self.signals.updateTime)
            self.addItem(item)

    # override
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.pos())
        if item:
            self.launchGame(item)

    # override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.removeGame(self.currentRow())
        elif event.key() == Qt.Key_Down and self.currentRow() == self.count() - 1:
            self.setCurrentRow(0)
        elif event.key() == Qt.Key_Up and self.currentRow() == 0:
            self.setCurrentRow(self.count() - 1)
        else:
            super().keyPressEvent(event)

    # override
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        item = self.itemAt(event.pos())
        self.signals.updateTime.emit(item)

        if item:
            item.context_menu.exec_(self.mapToGlobal(event.pos()))

    def gameClosed(self) -> None:
        self.dump()
        self.signals.gameClosed.emit()

    def removeGame(self, row: int) -> None:
        self.takeItem(row)

    def launchGame(self, item: ListWidgetItem) -> None:
        if item.exists():
            item.launchGame()

            self.signals.gameLaunched.emit()

    def errorLaunching(self, code: int) -> None:
        print("An error occurred while launching game with error code ", code)
        QCoreApplication.exit(-1)

    def addApp(self) -> None:
        path = QFileDialog.getOpenFileName(caption="Select game to add", filter="Applications (*.exe)")[0]
        if path:
            result = search('.+/(?P<name>.+).exe', path)
            if result:
                app = App(
                    {'title': result.group('name'),
                     'path': path,
                     'total_time':
                         {"hours": 0,
                          "minutes": 0
                          }
                     })
                item = ListWidgetItem(self)
                item.setApp(app)
                self.addItem(item)
                self.dump()
            else:
                print("Illegal path!")
                exit(-1)
        else:
            pass

    def all_items(self) -> list[ListWidgetItem]:
        for i in range(self.count()):
            yield self.item(i)

    def dump(self) -> None:
        with open(self._path, "w") as file:
            data = []
            for item in self.all_items():
                data.append(item.toJSON())

            json.dump(data, file)

    def load(self) -> list[dict[str, str] | dict[str, dict[str, int]]]:
        if not os.path.exists(self._path):
            os.makedirs("./data", exist_ok=True)
            with open(self._path, "w") as file:
                file.write("[]")

        if not os.path.exists(self._backup_path):
            with open(self._backup_path, "w") as file:
                file.write("[]")

        if os.path.getmtime(self._path) > os.path.getmtime(self._backup_path):
            self.backup_data()
        elif os.path.getmtime(self._path) < os.path.getmtime(self._backup_path):
            self.restore_data()

        try:
            with open(self._path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []

    def backup_data(self) -> None:
        shutil.copy(self._path, self._backup_path)

    def restore_data(self) -> None:
        shutil.copy(self._backup_path, self._path)
