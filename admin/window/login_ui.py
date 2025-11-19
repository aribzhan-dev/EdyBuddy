from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(360, 250)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoginWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.inputUser = QtWidgets.QLineEdit(LoginWindow)
        self.inputUser.setObjectName("inputUser")
        self.verticalLayout.addWidget(self.inputUser)
        self.inputPass = QtWidgets.QLineEdit(LoginWindow)
        self.inputPass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputPass.setObjectName("inputPass")
        self.verticalLayout.addWidget(self.inputPass)
        self.btnLogin = QtWidgets.QPushButton(LoginWindow)
        self.btnLogin.setObjectName("btnLogin")
        self.verticalLayout.addWidget(self.btnLogin)
        self.labelStatus = QtWidgets.QLabel(LoginWindow)
        self.labelStatus.setText("")
        self.labelStatus.setStyleSheet("color:red;")
        self.labelStatus.setObjectName("labelStatus")
        self.verticalLayout.addWidget(self.labelStatus)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "Login"))
        self.inputUser.setPlaceholderText(_translate("LoginWindow", "Username"))
        self.inputPass.setPlaceholderText(_translate("LoginWindow", "Password"))
        self.btnLogin.setText(_translate("LoginWindow", "Login"))
