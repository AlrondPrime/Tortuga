from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QFormLayout, QLineEdit, QPushButton


class _AppEditFormSignals(QObject):
    dataEdited = pyqtSignal(dict)


class AppEditForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit")
        self.setWindowIcon(QIcon("./resources/Shipwreck.ico"))
        self.setFixedSize(420, 116)
        self.signals = _AppEditFormSignals()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window |
                            Qt.WindowCloseButtonHint |
                            Qt.CustomizeWindowHint)
        form_layout = QFormLayout()
        self.title_field = QLineEdit()
        self.path_field = QLineEdit()

        form_layout.addRow("Title", self.title_field)
        form_layout.addRow("Path", self.path_field)
        save_btn = QPushButton("Save")
        save_btn.pressed.connect(self.onSavePressed)
        form_layout.addWidget(save_btn)
        self.setLayout(form_layout)

        desktop = QApplication.desktop()
        x = (desktop.width() - self.width() // 2) // 2
        y = (desktop.height() - self.height() // 2) // 2
        self.move(x, y)

    def onSavePressed(self) -> None:
        self.close()
        self.signals.dataEdited.emit({
            'title': self.title_field.text(),
            'path': self.path_field.text()
        })
