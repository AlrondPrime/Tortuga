from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QStyle, QApplication, QLabel, \
    QHBoxLayout, QWidget, QVBoxLayout, QToolBar, QToolButton, QSplitter

from ListWidget import ListWidget, getTime
from src.ListWidgetItem import ListWidgetItem


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Tortuga")

        # pixmap = QStyle.SP_MediaPlay
        # icon = self.style().standardIcon(pixmap)
        icon = QIcon("./resources/Shipwreck.ico")
        self.setWindowIcon(icon)

        desktop = QApplication.desktop()
        x = (desktop.width() - self.width() // 2) // 2
        y = (desktop.height() - self.height() // 2) // 2
        self.move(x, y)
        self.setFixedSize(278, 285)  # TODO refactor later

        self.label = QLabel("Total time:")

        self.textField = QLabel("N/A")

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.label)
        h_layout.addWidget(self.textField)

        h_container = QWidget()
        h_container.setLayout(h_layout)

        v_layout = QVBoxLayout()

        self.list = ListWidget()
        v_layout.addWidget(self.list)
        v_layout.addWidget(h_container)

        v_container = QWidget()
        v_container.setLayout(v_layout)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("Add app", self.list.addApp)

        hint_btn = QToolButton()
        pixmap2 = QStyle.SP_TitleBarContextHelpButton
        icon2 = self.style().standardIcon(pixmap2)
        hint_btn.setIcon(icon2)
        hint_btn.setDisabled(True)
        hint_btn.setToolTip("Enter to launch\nDel to remove\nF2 to rename")

        splitter = QSplitter(Qt.Horizontal)
        splitter.showMaximized()
        toolbar.addWidget(splitter)

        toolbar.addWidget(hint_btn)
        toolbar.setIconSize(QSize(16, 16))

        self.addToolBar(toolbar)
        self.setCentralWidget(v_container)

        self.list.itemClicked.connect(self.updateTime)
        self.list.currentItemChanged.connect(self.updateTime)
        self.list.signals.gameClosed.connect(self.gameClosed)
        self.list.signals.gameLaunched.connect(self.showMinimized)

    def closeEvent(self, event):
        self.list.dump()
        event.accept()

    def gameClosed(self, item: ListWidgetItem):
        self.updateTime(item)
        self.showNormal()

    def updateTime(self, item: ListWidgetItem):
        if item.isSelected():
            (hours, minutes) = getTime(item)
            self.textField.setText(str(hours) + "h " + str(minutes) + "m")
