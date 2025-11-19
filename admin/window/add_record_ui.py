from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddRecord(object):
    def setupUi(self, AddRecord):
        AddRecord.setObjectName("AddRecord")
        AddRecord.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddRecord)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.verticalLayout.addLayout(self.formLayout)
        self.btnSave = QtWidgets.QPushButton(AddRecord)
        self.btnSave.setObjectName("btnSave")
        self.verticalLayout.addWidget(self.btnSave)

        self.retranslateUi(AddRecord)
        QtCore.QMetaObject.connectSlotsByName(AddRecord)

    def retranslateUi(self, AddRecord):
        _translate = QtCore.QCoreApplication.translate
        AddRecord.setWindowTitle(_translate("AddRecord", "Add Record"))
        self.btnSave.setText(_translate("AddRecord", "Save"))
