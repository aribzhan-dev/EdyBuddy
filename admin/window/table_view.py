from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from admin.window.table_view_ui import Ui_TableView
from admin.window.add_record import AddRecordForm
from admin.db import Database

class TableViewWindow(QWidget):
    def __init__(self, table):
        super().__init__()
        self.table = table
        self.ui = Ui_TableView()
        self.ui.setupUi(self)

        self.db = Database()
        self.load_data()

        self.ui.btnAdd.clicked.connect(self.open_add_form)

    def load_data(self):
        rows = self.db.get_rows(self.table)
        cols = self.db.get_columns(self.table)

        self.ui.tableWidget.setColumnCount(len(cols))
        self.ui.tableWidget.setHorizontalHeaderLabels(cols)
        self.ui.tableWidget.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, col in enumerate(cols):
                self.ui.tableWidget.setItem(r, c, QTableWidgetItem(str(row[col])))

    def open_add_form(self):
        self.form = AddRecordForm(self.table)
        self.form.record_added.connect(self.load_data)
        self.form.show()