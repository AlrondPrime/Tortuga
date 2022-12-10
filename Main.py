import os, sys, re, time, psutil, json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor

class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        self.apps=[]
        self.path = R"Tortuga.json"
        # self.itemEntered.connect(self.itemHover)
        self.itemDoubleClicked.connect(self.sayHi)
        # self.itemActivated.connect(self.sayBye)
        self.itemChanged.connect(self.itemChange)
        self.load()
        for item in self.apps:
            item = QListWidgetItem(item['title'])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.addItem(item)
        self.setMouseTracking(True)

    def sayHi(self, item):
        print("hi")

    def itemActivated(self, item):
        print("bye")
        return super().itemActivated(item)

    def itemHover(self):
        pass
    # Launch game with time tracking
    def launchGame(self, item):
        item.setBackground( QColor(Qt.green) )
        # item.setBackground( QColor('#7fc97f') )
        # item.setBackground( QBrush(QColor('#7fc97f')) )

        i = self.row(item)
        now = time.time()
        if os.path.exists(self.apps[i]['path']):
            proc = psutil.Popen(self.apps[i]['path'])
            name = proc.name()
            proc.wait()
            for proc2 in psutil.process_iter():
                if proc2.name() == name:
                    print("cringe!")
                    proc2.wait()
        now2 = time.time()
        session_time = int(now2-now)
        hours = self.apps[i]['total_time']['hours']
        minutes = self.apps[i]['total_time']['minutes']
        minutes += session_time // 60
        if minutes >= 60:
            hours = minutes // 60
            minutes %= 60

        self.apps[i]['total_time']['hours'] = hours
        self.apps[i]['total_time']['minutes'] = minutes
        self.dump()
        item.setBackground( QColor(Qt.white) )

    def itemChange(self, item: QListWidgetItem) -> None:
        i = self.row(item)
        self.apps[i]['title'] = item.text()
        # return super().itemChanged(item)

    def addApp(self):
        path = QFileDialog.getOpenFileName(caption ="Select game to add", filter="Applications (*.exe)")[0]
        if path:
            result = re.search(r'.+/(?P<name>.+).exe', path)
            if result:
                self.apps.append({'title': result.group('name'), 'path': path, 'total_time': {"hours": 0, "minutes": 0}})
                self.addItem(result.group('name'))
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
        # super(MainWindow, self).__init__()   
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
        # self.showMinimized()
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
