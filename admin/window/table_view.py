from PyQt5.QtWidgets import (
    QWidget, QTableWidgetItem, QMenu, QAction, QMessageBox,
    QInputDialog, QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QCalendarWidget, QLineEdit
)
from PyQt5.QtCore import pyqtSignal
from admin.window.table_view_ui import Ui_TablePage
from admin.db import Database


class DateFilterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Date Range")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("From date:"))
        self.from_calendar = QCalendarWidget()
        layout.addWidget(self.from_calendar)

        layout.addWidget(QLabel("To date:"))
        self.to_calendar = QCalendarWidget()
        layout.addWidget(self.to_calendar)

        btns = QHBoxLayout()
        self.btn_apply = QPushButton("Apply")
        self.btn_cancel = QPushButton("Cancel")
        btns.addWidget(self.btn_apply)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_apply.clicked.connect(self.accept)

    def get_dates(self):
        d1 = self.from_calendar.selectedDate().toString("yyyy-MM-dd")
        d2 = self.to_calendar.selectedDate().toString("yyyy-MM-dd")
        return d1, d2



class TableViewWindow(QWidget):
    goBack = pyqtSignal()

    def __init__(self, table_name):
        super().__init__()
        self.ui = Ui_TablePage()
        self.ui.setupUi(self)

        self.table_name = table_name
        self.db = Database()

        self.columns = self.db.get_columns(table_name)

        # SIGNALS
        self.ui.btnAdd.clicked.connect(self.add_row)
        self.ui.btnFilter.clicked.connect(self.apply_filter)
        self.ui.inputSearch.textChanged.connect(self.search_filter)

        self.ui.tableWidget.setContextMenuPolicy(3)
        self.ui.tableWidget.customContextMenuRequested.connect(self.context_menu)
        self.ui.tableWidget.itemDoubleClicked.connect(self.edit_row)
        self.ui.btnBack.clicked.connect(lambda: self.goBack.emit())

        self.load_data()


    def load_data(self, rows=None):
        if rows is None:
            rows = self.db.get_rows(self.table_name)

        self.ui.tableWidget.setRowCount(len(rows))
        self.ui.tableWidget.setColumnCount(len(self.columns))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.columns)

        for r, row in enumerate(rows):
            for c, col in enumerate(self.columns):
                self.ui.tableWidget.setItem(r, c, QTableWidgetItem(str(row[col])))




    def search_filter(self):
        text = self.ui.inputSearch.text().strip()

        if not text:
            return self.load_data()

        sql_parts = [f"{col} ILIKE %s" for col in self.columns]
        query = f"SELECT * FROM {self.table_name} WHERE " + " OR ".join(sql_parts)
        params = [f"%{text}%"] * len(self.columns)

        rows = self.db.fetchall(query, params)
        self.load_data(rows)


    def apply_filter(self):
        options = []

        date_cols = [c for c in self.columns if c.lower() in
                     ["put_date", "date", "created_at", "updated_at", "deadline"]]

        if date_cols:
            options.append("Date")

        if "mark" in self.columns:
            options.append("Mark")

        if "liked" in self.columns:
            options.append("Liked")

        if not options:
            QMessageBox.information(self, "Нет фильтров", "Фильтры недоступны.")
            return

        chosen, ok = QInputDialog.getItem(self, "Фильтр", "Выберите:", options, 0, False)

        if not ok:
            return

        if chosen == "Date":
            self._filter_date(date_cols[0])
        elif chosen == "Mark":
            self._filter_mark()
        elif chosen == "Liked":
            self._filter_liked()



    def _filter_date(self, col):
        dialog = DateFilterDialog()

        if dialog.exec_() == QDialog.Accepted:
            d1, d2 = dialog.get_dates()

            q = f"SELECT * FROM {self.table_name} WHERE {col} BETWEEN %s AND %s"
            rows = self.db.fetchall(q, (d1, d2))

            self.load_data(rows)



    def _filter_mark(self):
        q = f"SELECT DISTINCT mark FROM {self.table_name} ORDER BY mark DESC"
        marks = [str(r["mark"]) for r in self.db.fetchall(q)]
        marks.insert(0, "All")

        chosen, ok = QInputDialog.getItem(self, "Оценки", "Выберите:", marks, 0, False)
        if not ok:
            return

        if chosen == "All":
            return self.load_data()

        q = f"SELECT * FROM {self.table_name} WHERE mark = %s"
        rows = self.db.fetchall(q, (chosen,))
        self.load_data(rows)



    def _filter_liked(self):
        options = ["All", "1 (Liked)", "0 (Not liked)"]

        chosen, ok = QInputDialog.getItem(self, "Liked", "Choose:", options, 0, False)
        if not ok:
            return

        if chosen == "All":
            return self.load_data()

        liked_value = 1 if chosen.startswith("1") else 0

        q = f"SELECT * FROM {self.table_name} WHERE liked = %s"
        rows = self.db.fetchall(q, (liked_value,))
        self.load_data(rows)



    def add_row(self):
        new_data = {}
        for col in self.columns:
            if col == "id":
                continue

            text, ok = QInputDialog.getText(self, "Добавить запись", f"{col}:")
            if not ok:
                return

            new_data[col] = text

        self.db.insert_row(self.table_name, new_data)
        self.load_data()



    def edit_row(self, item):
        row_index = item.row()
        row_id = self.ui.tableWidget.item(row_index, 0).text()

        updated = {}
        for i, col in enumerate(self.columns):
            if col == "id":
                continue

            old_val = self.ui.tableWidget.item(row_index, i).text()
            new_val, ok = QInputDialog.getText(self, f"Редактировать {col}", col, text=old_val)
            if not ok:
                return
            updated[col] = new_val

        set_clause = ", ".join([f"{col}=%s" for col in updated.keys()])
        params = list(updated.values()) + [row_id]

        q = f"UPDATE {self.table_name} SET {set_clause} WHERE id=%s"
        self.db.execute(q, params)

        self.load_data()



    def delete_row(self, row_index):
        row_id = self.ui.tableWidget.item(row_index, 0).text()

        confirm = QMessageBox.question(
            self, "Удалить?", "Вы уверены?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        q = f"DELETE FROM {self.table_name} WHERE id=%s"
        self.db.execute(q, (row_id,))
        self.load_data()



    def context_menu(self, pos):
        menu = QMenu(self)

        edit_action = QAction("Редактировать", self)
        delete_action = QAction("Удалить", self)

        menu.addAction(edit_action)
        menu.addAction(delete_action)

        row = self.ui.tableWidget.currentRow()
        action = menu.exec_(self.ui.tableWidget.mapToGlobal(pos))

        if row < 0:
            return

        if action == edit_action:
            self.edit_row(self.ui.tableWidget.item(row, 0))

        elif action == delete_action:
            self.delete_row(row)