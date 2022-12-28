from PyQt5.QtWidgets import *

from PackagesChecker import *
from src.MainWindow import MainWindow


def main():
    # os.system("cls")
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
