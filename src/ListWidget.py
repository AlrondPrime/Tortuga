import json
import sys
from pathlib import Path
from re import search

from PyQt5.QtCore import QThreadPool, Qt, QCoreApplication, QObject, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QColor
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFileDialog

from ThreadLaunch import ThreadLaunch


class ListSignals(QObject):
    gameLaunched = pyqtSignal(int)
    gameClosed = pyqtSignal(object)


class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        self.apps = []
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
        self.itemChanged.connect(self.itemChange)
        self.load()
        for item in self.apps:
            item = QListWidgetItem(item['title'])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
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

    def gameClosed(self, title):
        self.dump()
        for i, app in enumerate(self.apps):
            if app['title'] == title:
                self.setCurrentRow(i)
                self.item(i).setBackground(QColor(Qt.white))
                self.signals.gameClosed.emit(self.item(i))

    def removeGame(self, row: int):
        self.takeItem(row)
        self.apps.pop(row)

    def launchGame(self, item):
        item.setBackground(QColor(Qt.green))
        app = self.apps[self.row(item)]
        launcher = ThreadLaunch(app)
        launcher.signals.done.connect(self.gameClosed)
        launcher.signals.error.connect(self.errorLaunching)
        self.threadpool.start(launcher)
        self.signals.gameLaunched.emit(self.row(item))

    def errorLaunching(self, code):
        print("An error occurred while launching game with error code ", code)
        self.threadpool.clear()
        for i in range(self.count()):
            item = self.item(i)
            item.setBackground(QColor(Qt.white))

        QCoreApplication.exit(-1)

    def itemChange(self, item):
        i = self.row(item)
        self.apps[i]['title'] = item.text()

    def addApp(self):
        path = QFileDialog.getOpenFileName(caption="Select game to add", filter="Applications (*.exe)")[0]
        if path:
            result = search(r'.+/(?P<name>.+).exe', path)
            if result:
                self.apps.append(
                    {'title': result.group('name'), 'path': path, 'total_time': {"hours": 0, "minutes": 0}})
                item = QListWidgetItem(result.group('name'))
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.addItem(item)
                self.dump()
            else:
                print("Illegal path!")
                exit(-1)
        else:
            pass

    def dump(self):
        with open(self.path, "w") as file:
            json.dump(self.apps, file)

    def load(self):
        with open(self.path, "r") as file:
            self.apps = json.load(file)

    def getTime(self, item):
        i = self.row(item)
        return self.apps[i]['total_time']['hours'], self.apps[i]['total_time']['minutes']
