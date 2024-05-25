import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QWidget, QPushButton, QComboBox, QSpinBox, QLineEdit,
                             QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView, QTextEdit)

class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Database Viewer')

        self.loadButton = QPushButton('Load Database')
        self.loadButton.clicked.connect(self.openFileDialog)

        self.tableComboBox = QComboBox()
        self.tableComboBox.currentIndexChanged.connect(self.loadData) # Shake things up when table changes

        self.rowSpinBox = QSpinBox()
        self.rowSpinBox.setRange(1, 1000)
        self.rowSpinBox.setValue(10)
        self.rowSpinBox.valueChanged.connect(self.loadData)  # Update the dance floor when row count changes

        self.searchInput = QLineEdit()
        self.searchButton = QPushButton('Search')
        self.searchButton.clicked.connect(self.loadData)

        self.sqlInput = QTextEdit()
        self.sqlInput.setPlaceholderText("Enter your SQL query here...")
        self.sqlButton = QPushButton('Run SQL')
        self.sqlButton.clicked.connect(self.runSQLQuery)

        self.tableWidget = QTableWidget()
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.addButton = QPushButton('+')
        self.addButton.clicked.connect(self.addRow)

        layout = QVBoxLayout()
        layout.addWidget(self.loadButton)
        layout.addWidget(QLabel("Select Table:"))
        layout.addWidget(self.tableComboBox)
        layout.addWidget(QLabel("Number of Rows:"))
        layout.addWidget(self.rowSpinBox)

        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.searchInput)
        searchLayout.addWidget(self.searchButton)

        sqlLayout = QVBoxLayout()
        sqlLayout.addWidget(self.sqlInput)
        sqlLayout.addWidget(self.sqlButton)

        layout.addLayout(searchLayout)
        layout.addLayout(sqlLayout)
        layout.addWidget(self.tableWidget)
        layout.addWidget(self.addButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Database File", "", "SQLite Files (*.db);;All Files (*)", options=options)
        if fileName:
            self.database = fileName
            self.loadTables()

    def loadTables(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.tableComboBox.clear()
        for table in tables:
            self.tableComboBox.addItem(table[0])
        connection.close()
        self.loadData()  # Load data immediately after loading tables

    def loadData(self):
        if not hasattr(self, 'database'):
            return

        table = self.tableComboBox.currentText()
        if not table:
            return

        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns_info = cursor.fetchall()
        columns = [info[1] for info in columns_info]

        search_query = self.searchInput.text()
        if search_query:
            # Create a search query that looks in all columns
            search_conditions = ' OR '.join([f"{col} LIKE ?" for col in columns])
            query = f"SELECT * FROM {table} WHERE {search_conditions} LIMIT ?"
            params = [f'%{search_query}%'] * len(columns) + [self.rowSpinBox.value()]
            cursor.execute(query, params)
        else:
            query = f"SELECT * FROM {table} LIMIT ?"
            cursor.execute(query, (self.rowSpinBox.value(),))

        rows = cursor.fetchall()

        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(columns) + 1)  # Adding one for the delete button
        self.tableWidget.setHorizontalHeaderLabels(columns + ['Delete'])

        for rowIndex, row in enumerate(rows):
            for colIndex, col in enumerate(row):
                self.tableWidget.setItem(rowIndex, colIndex, QTableWidgetItem(str(col)))

            # Add a delete button to each row
            deleteButton = QPushButton('-')
            deleteButton.clicked.connect(lambda _, r=rowIndex: self.deleteRow(r))
            self.tableWidget.setCellWidget(rowIndex, len(columns), deleteButton)

        connection.close()

    def addRow(self):
        if not hasattr(self, 'database'):
            return

        table = self.tableComboBox.currentText()
        if not table:
            return

        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {table} DEFAULT VALUES")
        connection.commit()
        connection.close()
        self.loadData()

    def deleteRow(self, rowIndex):
        if not hasattr(self, 'database'):
            return

        table = self.tableComboBox.currentText()
        if not table:
            return

        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        row_id = self.tableWidget.item(rowIndex, 0).text()
        cursor.execute(f"DELETE FROM {table} WHERE rowid = ?", (row_id,))
        connection.commit()
        connection.close()
        self.loadData()

    def runSQLQuery(self):
        if not hasattr(self, 'database'):
            return

        query = self.sqlInput.toPlainText()
        if not query:
            return

        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        # Get column names
        columns = [description[0] for description in cursor.description]

        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)

        for rowIndex, row in enumerate(rows):
            for colIndex, col in enumerate(row):
                self.tableWidget.setItem(rowIndex, colIndex, QTableWidgetItem(str(col)))

        connection.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = DatabaseViewer()
    viewer.show()
    sys.exit(app.exec_())
