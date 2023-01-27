from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout


class TimeDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.radius = 10
        self.current_time_label = QLabel("N/A")
        self.total_time_label = QLabel("N/A")
        self.current_time_label.setAlignment(Qt.AlignRight)
        self.total_time_label.setAlignment(Qt.AlignRight)
        self.time_layout = QFormLayout()
        self.time_layout.addRow("Current session time:", self.current_time_label)
        self.time_layout.addRow("Total played time:", self.total_time_label)
        self.setLayout(self.time_layout)

    # override
    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.end()

        super().paintEvent(e)
