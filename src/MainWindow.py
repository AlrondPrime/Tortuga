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
        desktop = QApplication.desktop()
        x = (desktop.width() - self.width() // 2) // 2
        y = (desktop.height() - self.height() // 2) // 2
        self.move(x, y)
        self.setFixedSize(278, 285)

        self.tray_icon = SystemTrayIcon()

        self.list = ListWidget()

        # Time layout
        self.current_time_label = QLabel("N/A")
        self.total_time_label = QLabel("N/A")
        time_layout = QFormLayout()
        time_layout.addRow("Current session time:", self.current_time_label)
        time_layout.addRow("Total played time:", self.total_time_label)

        # Toolbar
        hint_btn = QToolButton()
        pixmap2 = QStyle.SP_TitleBarContextHelpButton
        icon2 = self.style().standardIcon(pixmap2)
        hint_btn.setIcon(icon2)
        hint_btn.setDisabled(True)
        hint_btn.setToolTip("Enter to launch\nDel to remove\nF2 to rename")

        splitter = QSplitter(Qt.Horizontal)
        splitter.showMaximized()

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("Add app", self.list.addApp)
        toolbar.addWidget(splitter)
        toolbar.addWidget(hint_btn)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Central widget
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.list)
        v_layout.addLayout(time_layout)
        central_widget = QWidget()
        central_widget.setLayout(v_layout)
        self.setCentralWidget(central_widget)

        self.list.itemClicked.connect(self.updateTime)
        self.list.currentItemChanged.connect(self.updateTime)
        self.list.signals.updateTime.connect(self.updateTime)
        self.list.signals.gameClosed.connect(self.showNormal)
        self.list.signals.gameLaunched.connect(self.hide)
        self.tray_icon.signals.showWindow.connect(self.showNormal)
        self.tray_icon.signals.closeWindow.connect(self.exit)
        self.tray_icon.activated.connect(self.tray_icon.activateEvent)

    def exit(self) -> None:
        self.tray_icon.hide()
        self.list.dump()
        self.close()
        QApplication.exit(0)

    # override
    def closeEvent(self, event) -> None:
        self.hide()
        event.ignore()

    def updateTime(self, item: ListWidgetItem) -> None:
        if item.isSelected():
            (hours, minutes) = item.currentTime()
            self.current_time_label.setText(str(hours) + "h " + str(minutes) + "m")
            (hours, minutes) = item.totalTime()
            self.total_time_label.setText(str(hours) + "h " + str(minutes) + "m")
