import json
import sys
from json import JSONDecodeError
from pathlib import Path
from re import search

from PyQt5.QtCore import QThreadPool, Qt, QCoreApplication, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QColor
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFileDialog

from ThreadLaunch import ThreadLaunch
from ListWidgetItem import ListWidgetItem
from src.App import App


class ListSignals(QObject):
    gameLaunched = pyqtSignal()
    gameClosed = pyqtSignal(object)


def getTime(item):
    return item.getTime()


def itemChange(item):
    item.setTitle(item.text())


class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        # if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        #     bundle_dir = Path(sys._MEIPASS)
        # else:
        #     bundle_dir = Path(__file__).parent
        #
        # self.path = Path.cwd() / bundle_dir / "Tortuga.json"
        # self.path = Path(__file__).resolve().with_name("Tortuga.json")
        self.path = R"Tortuga.json"
        self.threadpool = QThreadPool()
        self.signals = ListSignals()
        self.itemActivated.connect(self.launchGame)
        self.itemChanged.connect(itemChange)

        for item in self.load_json():
            app = App(item)
            item = ListWidgetItem(item['title'])
            item.setApp(app)
            self.addItem(item)

        self.setMouseTracking(True)

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        item = self.itemAt(e.pos())
        if item:
            self.launchGame(item)
            e.accept()
        else:
            e.ignore()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Delete:
            self.removeGame(self.currentRow())
            e.accept()

        return super().keyPressEvent(e)

    def gameClosed(self, title: str):
        self.dump()
        for item in self.findItems(title, Qt.MatchRegExp):
            item.setBackground(QColor(Qt.white))
            self.signals.gameClosed.emit(item)

    def removeGame(self, row: int):
        self.takeItem(row)

    def launchGame(self, item):
        item.setBackground(QColor(Qt.green))
        item.launchGame()
        item.signals.gameClosed.connect(self.gameClosed)

        self.signals.gameLaunched.emit()

    def errorLaunching(self, code):
        print("An error occurred while launching game with error code ", code)
        self.threadpool.clear()
        for i in range(self.count()):
            item = self.item(i)
            item.setBackground(QColor(Qt.white))

        QCoreApplication.exit(-1)

    def addApp(self):
        path = QFileDialog.getOpenFileName(caption="Select game to add", filter="Applications (*.exe)")[0]
        if path:
            result = search(r'.+/(?P<name>.+).exe', path)
            if result:
                app = App(
                    {'title': result.group('name'), 'path': path, 'total_time': {"hours": 0, "minutes": 0}})
                item = ListWidgetItem(result.group('name'))
                item.setApp(app)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.addItem(item)
                self.dump()
            else:
                print("Illegal path!")
                exit(-1)
        else:
            pass

    def all_items(self):
        for i in range(self.count()):
            yield self.item(i)

    def dump(self):
        with open(self.path, "w") as file:
            data = []
            for item in self.all_items():
                data.append(item.toJSON())

            json.dump(data, file)

    def load_json(self):
        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except JSONDecodeError:
            return []
