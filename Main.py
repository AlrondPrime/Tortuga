import json
import psutil
import time
from re import search

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PackagesChecker import *


class LauncherSignals(QObject):
    done = pyqtSignal(object)
    error = pyqtSignal(int)


class ListSignals(QObject):
    gameLaunched = pyqtSignal(int)
    gameClosed = pyqtSignal(object)


class ThreadLaunch(QRunnable):
    def __init__(self, app):
        super(QRunnable, self).__init__()
        self.app = app
        self.signals = LauncherSignals()

    def run(self):
        now = time.time()
        if os.path.exists(self.app['path']):
            result = search(r'(?P<name>.+)/.+.exe', self.app['path'])

            if not result:
                print("Error with path")
                self.signals.error.emit(-1)
                return

            proc = psutil.Popen([], executable=self.app['path'], cwd=result.group('name'))
            name = proc.name()
            proc.wait()
            for proc2 in psutil.process_iter():
                if proc2.name() == name:
                    print("cringe!")
                    proc2.wait()
        now2 = time.time()
        session_time = int(now2 - now)
        hours = self.app['total_time']['hours']
        minutes = self.app['total_time']['minutes']
        minutes += session_time // 60
        if minutes >= 60:
            hours += minutes // 60
            minutes %= 60

        self.app['total_time']['hours'] = hours
        self.app['total_time']['minutes'] = minutes
        self.signals.done.emit(self.app['title'])


class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        self.apps = []
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
        t = self.takeItem(row)
        del t
        self.apps.pop(row)

    # Launch game with time tracking
    def launchGame(self, item):
        item.setBackground(QColor(Qt.green))
        app = self.apps[self.row(item)]
        launcher = ThreadLaunch(app)
        launcher.signals.done.connect(self.gameClosed)
        launcher.signals.error.connect(self.errorLaunching)
        self.threadpool.start(launcher)
        self.signals.gameLaunched.emit(self.row(item))

    def errorLaunching(self, code):
        print("Can't launch game, an error occured")
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


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Tortuga")

        pixmap = getattr(QStyle, "SP_MediaPlay")
        icon = self.style().standardIcon(pixmap)
        self.setWindowIcon(icon)

        desktop = QApplication.desktop()
        x = (desktop.width() - self.width() // 2) // 2
        y = (desktop.height() - self.height() // 2) // 2
        self.move(x, y)

        self.label = QLabel("Total time:")

        self.textField = QLabel()

        Hlayout = QHBoxLayout()
        Hlayout.addWidget(self.label)
        Hlayout.addWidget(self.textField)

        Hcontainer = QWidget()
        Hcontainer.setLayout(Hlayout)

        Vlayout = QVBoxLayout()

        self.list = ListWidget()
        Vlayout.addWidget(self.list)
        Vlayout.addWidget(Hcontainer)

        Vcontainer = QWidget()
        Vcontainer.setLayout(Vlayout)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("Add app", self.list.addApp)
        self.addToolBar(toolbar)

        self.setCentralWidget(Vcontainer)

        self.list.itemClicked.connect(self.updateTime)
        self.list.signals.gameClosed.connect(self.gameClosed)
        self.list.signals.gameLaunched.connect(self.showMinimized)

    def closeEvent(self, event):
        print("close")
        self.list.dump()
        event.accept()

    def exitEvent(self, event):
        print("exit")
        event.accept()

    def gameClosed(self, item):
        self.updateTime(item)
        self.showNormal()

    def updateTime(self, item):
        # Update time
        (hours, minutes) = self.list.getTime(item)
        self.textField.setText(str(hours) + "h " + str(minutes) + "m")

def main():
    # os.system("cls")
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
