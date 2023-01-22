from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QStyle, QApplication, QLabel, \
    QWidget, QVBoxLayout, QToolBar, QToolButton, QSplitter, QFormLayout

from ListWidget import ListWidget
from ListWidgetItem import ListWidgetItem
from SystemTrayIcon import SystemTrayIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tortuga")
        self.setWindowIcon(QIcon("./resources/Shipwreck.ico"))
        self.tray_icon = SystemTrayIcon()

        desktop = QApplication.desktop()
        x = (desktop.width() - self.width() // 2) // 2
        y = (desktop.height() - self.height() // 2) // 2
        self.move(x, y)
        self.setFixedSize(278, 285)  # TODO refactor later

        self.current_time_label = QLabel("N/A")
        self.total_time_label = QLabel("N/A")

        time_layout = QFormLayout()
        time_layout.addRow("Current session time:", self.current_time_label)
        time_layout.addRow("Total played time:", self.total_time_label)

        self.list = ListWidget()

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.list)
        v_layout.addLayout(time_layout)

        central_widget = QWidget()
        central_widget.setLayout(v_layout)

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
        self.setCentralWidget(central_widget)

        self.list.itemClicked.connect(self.updateTime)
        self.list.currentItemChanged.connect(self.updateTime)
        self.list.signals.updateTime.connect(self.updateTime)
        self.list.signals.gameClosed.connect(self.showNormal)
        self.list.signals.gameLaunched.connect(self.showMinimized)
        self.tray_icon.showWindow.connect(self.show)
        self.tray_icon.closeWindow.connect(self.exit)

    def exit(self):
        self.list.dump()
        self.tray_icon.hide()
        self.close()

        QApplication.exit(0)

    def closeEvent(self, event):
        self.hide()

        event.ignore()

    def updateTime(self, item: ListWidgetItem):
        if item.isSelected():
            (hours, minutes) = item.currentTime()
            self.current_time_label.setText(str(hours) + "h " + str(minutes) + "m")
            (hours, minutes) = item.totalTime()
            self.total_time_label.setText(str(hours) + "h " + str(minutes) + "m")
