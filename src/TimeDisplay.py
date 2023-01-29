from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout, QFrame

from Helpers import Style


class TimeDisplay(QFrame):
    def __init__(self):
        super().__init__()
        self.current_time_label = QLabel("Current session time:")
        self.total_time_label = QLabel("Total played time:")
        self.current_time_field = QLabel("N/A")
        self.total_time_field = QLabel("N/A")
        self.current_time_field.setAlignment(Qt.AlignRight)
        self.total_time_field.setAlignment(Qt.AlignRight)
        self.time_layout = QFormLayout()
        self.time_layout.addRow(self.current_time_label, self.current_time_field)
        self.time_layout.addRow(self.total_time_label, self.total_time_field)
        self.setLayout(self.time_layout)
        self.setStyleSheet(Style("./styles/TimeDisplay.qss"))
