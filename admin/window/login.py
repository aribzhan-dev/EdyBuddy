from PyQt5.QtWidgets import QWidget
from admin.window.login_ui import Ui_LoginWindow
from admin.window.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.ui.btnLogin.clicked.connect(self.do_login)

    def do_login(self):
        user = self.ui.inputUser.text().strip().lower()
        pwd = self.ui.inputPass.text()

        if user == "admin" and pwd == "1234":
            self.main = MainWindow()
            self.main.show()
            self.close()
        else:
            self.ui.labelStatus.setText("Incorrect login")