import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle

from admin.window.login import LoginWindow


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    win = LoginWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()