from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5.QtCore import pyqtSignal
from admin.window.add_record_ui import Ui_AddRecord
from admin.db import Database


class AddRecordForm(QWidget):
    record_added = pyqtSignal()

    def __init__(self, table):
        super().__init__()
        self.ui = Ui_AddRecord()
        self.ui.setupUi(self)

        self.table = table
        self.db = Database()

        self.inputs = {}


        cols = self.db.get_columns(table)
        cols = [c for c in cols if c != "id"]

        form_layout = self.ui.formLayout

        for col in cols:
            field = QLineEdit()
            field.setPlaceholderText(col)
            form_layout.addRow(col, field)
            self.inputs[col] = field

        self.ui.btnSave.clicked.connect(self.save)

    def save(self):

        data = {col: inp.text() for col, inp in self.inputs.items()}


        self.db.insert_row(self.table, data)

        self.record_added.emit()
        self.close()