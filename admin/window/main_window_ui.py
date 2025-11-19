from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.mainLayout = QtWidgets.QHBoxLayout(MainWindow)
        self.mainLayout.setObjectName("mainLayout")
        self.tableList = QtWidgets.QListWidget(MainWindow)
        self.tableList.setMinimumWidth(280)
        self.tableList.setMaximumWidth(280)
        self.tableList.setObjectName("tableList")
        self.mainLayout.addWidget(self.tableList)
        self.pages = QtWidgets.QStackedWidget(MainWindow)
        self.pages.setObjectName("pages")
        self.mainLayout.addWidget(self.pages)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Admin Panel"))
