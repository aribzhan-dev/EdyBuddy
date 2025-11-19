
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TableView(object):
    def setupUi(self, TableView):
        TableView.setObjectName("TableView")
        TableView.resize(700, 500)
        self.verticalLayout = QtWidgets.QVBoxLayout(TableView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(TableView)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.btnAdd = QtWidgets.QPushButton(TableView)
        self.btnAdd.setObjectName("btnAdd")
        self.verticalLayout.addWidget(self.btnAdd)

        self.retranslateUi(TableView)
        QtCore.QMetaObject.connectSlotsByName(TableView)

    def retranslateUi(self, TableView):
        _translate = QtCore.QCoreApplication.translate
        TableView.setWindowTitle(_translate("TableView", "Table Viewer"))
        self.btnAdd.setText(_translate("TableView", "Add New Record"))
