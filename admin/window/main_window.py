from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidgetItem
from admin.window.main_window_ui import Ui_MainWindow
from admin.db import Database
from admin.window.table_view import TableViewWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Database
        self.db = Database()

        # ======================
        # 1) TABLE LIST PAGE
        # ======================

        # Sidebar already exists in ui: tableList
        self.tables_page = QWidget()
        self.tables_layout = QVBoxLayout(self.tables_page)
        self.tables_layout.setContentsMargins(0, 0, 0, 0)
        self.tables_layout.addWidget(self.ui.tableList)

        # Add it to stacked widget
        self.ui.pages.addWidget(self.tables_page)
        self.ui.pages.setCurrentWidget(self.tables_page)

        # Load table names
        self.load_tables()

        # Open table on double click
        self.ui.tableList.itemDoubleClicked.connect(self.open_table)

        # ======================
        # SIDEBAR STYLE (UI)
        # ======================
        self._apply_sidebar_style()


    # ==========================
    # LOAD TABLE LIST
    # ==========================
    def load_tables(self):
        tables = self.db.get_tables()
        print("Tables:", tables)
        self.ui.tableList.clear()

        for t in tables:
            item = QListWidgetItem(t)
            self.ui.tableList.addItem(item)


    # ==========================
    # OPEN TABLE PAGE
    # ==========================
    def open_table(self, item):
        table = item.text()
        self.table_page = TableViewWindow(table)

        # Back signal
        self.table_page.goBack.connect(self.show_tables_page)

        # Add to stacked widget
        self.ui.pages.addWidget(self.table_page)
        self.ui.pages.setCurrentWidget(self.table_page)


    # ==========================
    # RETURN BACK TO TABLE LIST
    # ==========================
    def show_tables_page(self):
        self.ui.pages.setCurrentWidget(self.tables_page)


    # ==========================
    # SIDEBAR BEAUTIFUL DESIGN
    # ==========================
    def _apply_sidebar_style(self):
        style = """
        QListWidget {
            background-color: #1e2833;
            border: 1px solid #3a4a5a;
            padding: 8px;
            font-size: 17px;
            color: #d6d9df;
        }

        QListWidget::item {
            padding: 12px 12px;
            margin: 3px 0;
            border-radius: 6px;
        }

        QListWidget::item:hover {
            background-color: #2f3c4a;
        }

        QListWidget::item:selected {
            background-color: #34699a;
            color: white;
        }

        QListWidget {
            border-right: 2px solid #3a4a5a;
            font-family: -apple-system, "SF Pro Display", "Roboto", sans-serif;
            font-weight: 500;
            font-size: 17px;
        }
        """

        self.ui.tableList.setFixedWidth(280)
        self.ui.tableList.setStyleSheet(style)