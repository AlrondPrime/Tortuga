import sys
import os.path
from pathlib import Path
import shutil
import json
from json import JSONDecodeError
from re import search

from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QColor
from PyQt5.QtWidgets import QListWidget, QFileDialog

from ListWidgetItem import ListWidgetItem
from App import App


class ListSignals(QObject):
    gameLaunched = pyqtSignal()
    gameClosed = pyqtSignal()
    updateTime = pyqtSignal(object)


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
        self.path = R"./data/Tortuga.json"
        self.backup_path = R"./data/Tortuga-backup.json"
        self.signals = ListSignals()
        self.itemActivated.connect(self.launchGame)
        self.itemChanged.connect(itemChange)

        for item in self.load():
            app = App(item)
            item = ListWidgetItem(item['title'])
            item.setApp(app)
            item.signals.updateTime.connect(self.signals.updateTime)
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

    def gameClosed(self):
        self.dump()
        self.signals.gameClosed.emit()

    def removeGame(self, row: int):
        self.takeItem(row)

    def launchGame(self, item: ListWidgetItem):
        item.launchGame()
        item.signals.gameClosed.connect(self.gameClosed)

        self.signals.gameLaunched.emit()

    def errorLaunching(self, code: int):
        print("An error occurred while launching game with error code ", code)

        for i in range(self.count()):
            item = self.item(i)
            item.setBackground(QColor(Qt.white))

        QCoreApplication.exit(-1)

    def addApp(self):
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
                item = ListWidgetItem(result.group('name'))
                item.signals.updateTime.connect(self.signals.updateTime)
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

    def dump(self):
        with open(self.path, "w") as file:
            data = []
            for item in self.all_items():
                data.append(item.toJSON())

            json.dump(data, file)

    def load(self):
        if not os.path.exists(self.path):
            os.makedirs("./data", exist_ok=True)
            with open(self.path, "w") as file:
                file.write("[]")

        if not os.path.exists(self.backup_path):
            with open(self.backup_path, "w") as file:
                file.write("[]")

        if os.path.getmtime(self.path) > os.path.getmtime(self.backup_path):
            self.backup_data()
        elif os.path.getmtime(self.path) < os.path.getmtime(self.backup_path):
            self.restore_data()

        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except JSONDecodeError:
            return []

    def backup_data(self):
        shutil.copy(self.path, self.backup_path)

    def restore_data(self):
        shutil.copy(self.backup_path, self.path)
