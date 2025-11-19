from PyQt5.QtWidgets import QMainWindow
from admin.window.login_ui import Ui_LoginWindow
from admin.window.main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.ui.btnLogin.clicked.connect(self.login)

    def login(self):
        user = self.ui.inputUser.text()
        pwd = self.ui.inputPass.text()

        if user == "admin" and pwd == "1234":
            self.main = MainWindow()
            self.main.show()
            self.close()
        else:
            self.ui.labelStatus.setText("Incorrect login")