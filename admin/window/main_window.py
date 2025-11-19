from PyQt5.QtWidgets import QMainWindow
from admin.window.main_window_ui import Ui_MainWindow
from admin.window.table_view import TableViewWindow
from admin.db import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = Database()

        self.load_tables()
        self.ui.tableList.itemDoubleClicked.connect(self.open_table)

    def load_tables(self):
        tables = self.db.get_tables()
        self.ui.tableList.clear()
        for t in tables:
            self.ui.tableList.addItem(t)

    def open_table(self, item):
        table_name = item.text()
        self.tableWindow = TableViewWindow(table_name)
        self.tableWindow.show()