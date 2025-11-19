from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(350, 220)
        self.mainLayout = QtWidgets.QVBoxLayout(LoginWindow)
        self.mainLayout.setObjectName("mainLayout")
        self.inputUser = QtWidgets.QLineEdit(LoginWindow)
        self.inputUser.setObjectName("inputUser")
        self.mainLayout.addWidget(self.inputUser)
        self.inputPass = QtWidgets.QLineEdit(LoginWindow)
        self.inputPass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputPass.setObjectName("inputPass")
        self.mainLayout.addWidget(self.inputPass)
        self.btnLogin = QtWidgets.QPushButton(LoginWindow)
        self.btnLogin.setMinimumHeight(40)
        self.btnLogin.setObjectName("btnLogin")
        self.mainLayout.addWidget(self.btnLogin)
        self.labelStatus = QtWidgets.QLabel(LoginWindow)
        self.labelStatus.setText("")
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.mainLayout.addWidget(self.labelStatus)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "Login"))
        self.inputUser.setPlaceholderText(_translate("LoginWindow", "Username"))
        self.inputPass.setPlaceholderText(_translate("LoginWindow", "Password"))
        self.btnLogin.setText(_translate("LoginWindow", "Login"))
        self.labelStatus.setStyleSheet(_translate("LoginWindow", "color:red;"))
