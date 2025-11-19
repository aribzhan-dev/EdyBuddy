import sys
from PyQt5.QtWidgets import QApplication
from window.login import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())