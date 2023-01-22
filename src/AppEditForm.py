from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QFormLayout, QLineEdit, QPushButton, QDialog


class AppEditForm(QWidget):
    dataEdited = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit")
        self.setWindowIcon(QIcon("./resources/Shipwreck.ico"))
        self.setFixedSize(420, 116)

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

    def onSavePressed(self):
        self.close()

        self.dataEdited.emit({
            'title': self.title_field.text(),
            'path': self.path_field.text()
        })
