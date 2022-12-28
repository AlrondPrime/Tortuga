from PyQt5.QtWidgets import QMainWindow, QStyle, QApplication, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QToolBar

from ListWidget import ListWidget


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

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.label)
        hlayout.addWidget(self.textField)

        hcontainer = QWidget()
        hcontainer.setLayout(hlayout)

        vlayout = QVBoxLayout()

        self.list = ListWidget()
        vlayout.addWidget(self.list)
        vlayout.addWidget(hcontainer)

        vcontainer = QWidget()
        vcontainer.setLayout(vlayout)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("Add app", self.list.addApp)
        self.addToolBar(toolbar)

        self.setCentralWidget(vcontainer)

        self.list.itemClicked.connect(self.updateTime)
        self.list.currentItemChanged.connect(self.updateTime)
        self.list.signals.gameClosed.connect(self.gameClosed)
        self.list.signals.gameLaunched.connect(self.showMinimized)

    def closeEvent(self, event):
        print("close")
        self.list.dump()
        event.accept()

    def gameClosed(self, item):
        self.updateTime(item)
        self.showNormal()

    def updateTime(self, item):
        (hours, minutes) = self.list.getTime(item)
        self.textField.setText(str(hours) + "h " + str(minutes) + "m")
