import os, sys, time, psutil, json
from re import search
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor

class launcherSignals(QObject):
    done = pyqtSignal(object)

class threadLaunch(QRunnable):  
    def __init__(self, app):
        super(QRunnable, self).__init__()
        self.app = app
        self.signals = launcherSignals()

    def run(self):
        now = time.time()
        if os.path.exists(self.app['path']):
            result = search(r'(?P<name>.+)/.+.exe', self.app['path'])
            proc = psutil.Popen([], executable=self.app['path'], cwd = result.group('name'))
            name = proc.name()
            proc.wait()
            for proc2 in psutil.process_iter():
                if proc2.name() == name:
                    print("cringe!")
                    proc2.wait()
        now2 = time.time()
        session_time = int(now2-now)
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
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.apps=[]
        self.path = R"Tortuga.json"
        self.threadpool = QThreadPool()
        self.itemActivated.connect(self.launchGame)
        self.itemChanged.connect(self.itemChange)

        self.load()
        for item in self.apps:
            item = QListWidgetItem(item['title'])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.addItem(item)
        self.setMouseTracking(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.removeGame(self.currentRow())
            event.accept()
        else:
            super().keyPressEvent(event)

    def gameClosed(self, title):
        self.dump()
        for i, item in enumerate(self.apps):
            if item['title'] == title:
                self.item(i).setBackground( QColor(Qt.white) )

    def removeGame(self, row:int):
        t = self.takeItem(row)
        del t
        self.apps.pop(row)

    # Launch game with time tracking
    def launchGame(self, item):
        item.setBackground( QColor(Qt.green) )
        app = self.apps[ self.row(item) ]
        launcher = threadLaunch(app)
        launcher.signals.done.connect(self.gameClosed)
        self.threadpool.start(launcher) 

    def itemChange(self, item):
        i = self.row(item)
        self.apps[i]['title'] = item.text()

    def addApp(self):
        path = QFileDialog.getOpenFileName(caption ="Select game to add", filter="Applications (*.exe)")[0]
        if path:
            result = search(r'.+/(?P<name>.+).exe', path)
            if result:
                self.apps.append({'title': result.group('name'), 'path': path, 'total_time': {"hours": 0, "minutes": 0}})
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
        return (self.apps[i]['total_time']['hours'], self.apps[i]['total_time']['minutes'])

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
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

        self.list.itemClicked.connect(self.itemClick)

    def closeEvent(self, event):
        self.list.dump()
        event.accept()

    def exitEvent(self, event):
        print("exit")
        event.accept()
    
    def itemClick(self, item):
        (hours, minutes) = self.list.getTime(item)
        self.textField.setText(str(hours) + "h " + str(minutes) + "m")

def main():
    os.system("cls")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
