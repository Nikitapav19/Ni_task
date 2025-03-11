import os
import sqlite3
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox

from app import (CheckCategoriesWidget,
                         CreateTaskWidget, CreateCategoryWidget, CheckFinishedTasksWidget, CheckInfoOfTask)


class MainWindowFunctionality:
    """
    Основной функционал окна
    Вызовы функций из app.py
    Описание функционала кнопок основного окна
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.initUi()

    def initUi(self):
        """
        Основная инициализация
        Все init производят инициализации
        """
        self.initTable()

        self.check_for_date()

        self.main_window.groupBox.setVisible(False)
        self.main_window.menu_button.clicked.connect(self.clicked_menu_button)
        self.main_window.create_task.clicked.connect(self.create_task)
        self.main_window.create_category.clicked.connect(self.create_category)
        self.main_window.check_categories.clicked.connect(self.check_categories)
        self.main_window.info_button.setEnabled(False)

        self.main_window.tableWidget.cellDoubleClicked.connect(self.info_double_clicked_button)
        self.main_window.info_button.clicked.connect(self.info_clicked_button)
        self.main_window.check_finished_tasks.clicked.connect(self.check_finished_tasks)
        self.main_window.update_table.clicked.connect(self.initTable)

        self.main_window.instruction_action.triggered.connect(self.instruction_action)

    def initTable(self):
        table = ['Название', 'Категория', 'Сроки', 'Приоритет', 'Выполнено']
        self.main_window.tableWidget.setColumnCount(5)
        for i, word in enumerate(table):
            self.main_window.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(word))
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        result = cur.execute('''SELECT Tasks.title, Categories.category_name,
                                Tasks.deadline, Tasks.priority, Tasks.status FROM Tasks
                                INNER JOIN Categories ON Tasks.categories = Categories.category_id
                                WHERE Tasks.status = 0''').fetchall()
        self.main_window.tableWidget.setRowCount(len(result))
        for i, row in enumerate(result):
            for j in range(len(row)):
                if j == 4:
                    check_box = QCheckBox()
                    check_box.setChecked(False)
                    check_box.clicked.connect(lambda state, i=i: self.check_box_clicked(i))
                    self.main_window.tableWidget.setCellWidget(i, j, check_box)
                else:
                    item = QTableWidgetItem(row[j])
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.main_window.tableWidget.setItem(i, j, item)
        self.check_for_date()
        self.main_window.tableWidget.cellClicked.connect(self.selected_cell)

    def selected_cell(self, row: int, column: int):
        """
        Проверяет выбранную ячейку
        """
        if column == 0:
            self.main_window.info_button.setEnabled(True)
        else:
            self.main_window.info_button.setEnabled(False)

    def check_for_date(self):
        """
        Запись данных в таблицу о текущем времени пользователя
        Эти данные пригодятся для реализаци затраченного времени на задачу
        """
        current_time = datetime.now()
        tasks = []
        for i in range(self.main_window.tableWidget.rowCount()):
            task_time = datetime.strptime(self.main_window.tableWidget.item(i, 2).text(), "%d-%m-%Y")
            time_difference = task_time - current_time
            tasks.append((time_difference, i))

        if len(tasks) > 0:
            closest_task = min(tasks)
            if closest_task[0] < timedelta(days=0):
                self.main_window.statusbar.showMessage('У вас есть истекшие задачи')
            elif timedelta(days=0) <= closest_task[0] <= timedelta(days=1):
                self.main_window.statusbar.showMessage('Сегодня заканчиваются сроки задач!')
            elif timedelta(days=0) <= closest_task[0] <= timedelta(days=3):
                self.main_window.statusbar.showMessage('Проверьте сроки задач, они скоро истекут!')
            elif timedelta(days=0) <= closest_task[0] <= timedelta(days=7):
                self.main_window.statusbar.showMessage('На этой неделе истекают задачи')
            else:
                self.main_window.statusbar.showMessage('У вас все в порядке!')

    def check_box_clicked(self, row: int):
        """
        Пользователь нажал на кнопку
        Смена значений в БД, запись времени
        """
        check_box = self.main_window.tableWidget.cellWidget(row, 4)
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        item = str(self.main_window.tableWidget.item(row, 0).text())
        deadline = self.main_window.tableWidget.item(row, 2).text()
        end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        start_time_str = cur.execute('SELECT start_time FROM Tasks WHERE title = ? AND deadline = ?',
                                     (item, deadline, )).fetchall()[0][0]
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        time_spent = end_time - start_time
        if check_box is not None:
            if check_box.isChecked():
                cur.execute('UPDATE Tasks SET status = 1 WHERE title = ? AND deadline = ?',
                            (item, deadline, ))
                cur.execute('UPDATE Tasks SET end_time = ? WHERE title = ? AND deadline = ?',
                            (end_time, item, deadline, ))
                cur.execute('UPDATE Tasks SET time_spent = ? WHERE title = ? AND deadline = ?',
                            (str(time_spent), item, deadline, ))
            else:
                cur.execute('UPDATE Tasks SET status = 0 WHERE title = ? AND deadline = ?',
                            (item, deadline, ))
            con.commit()
            con.close()

    def instruction_action(self):
        """
        Функция открывает инструкцию о приложении README.txt
        """
        current_dir = os.getcwd()
        readme_path = os.path.join(current_dir, "README.txt")
        os.startfile(readme_path)

    def clicked_menu_button(self):
        """
        Пользователь нажал на кнопку 'меню'
        Открывает основной функционал с кнопками
        """
        if self.main_window.groupBox.isVisible():
            self.main_window.groupBox.setVisible(False)
        else:
            self.main_window.groupBox.setVisible(True)

    def info_clicked_button(self):
        """
        Пользователь нажал на кнопку 'подробнее'
        Вызывает класс, который выводит виждет с информацией
        """
        items = self.main_window.tableWidget.selectedItems()
        selected_item = [item.text() for item in items]
        if selected_item:
            self.info_clicked_widget = CheckInfoOfTask(selected_item[0])
        else:
            self.info_clicked_widget = CheckInfoOfTask()
            self.main_window.info_button.setEnabled(False)
        self.info_clicked_widget.show()

    def info_double_clicked_button(self, row: int, column: int):
        """
        Пользователь нажал двойным кликом на название
        Вызывает класс, который выводит виждет с информацией
        """
        selected_item = [item.text() for item in self.main_window.tableWidget.selectedItems()]
        if column != 0:
            return None
        elif selected_item:
            self.info_clicked_widget = CheckInfoOfTask(selected_item[0])
        else:
            self.info_clicked_widget = CheckInfoOfTask()
        self.info_clicked_widget.show()

    """
    Далее идут вызовы классов, отвечающие за виджеты
    """

    def create_task(self):
        self.create_task_widget = CreateTaskWidget()
        self.create_task_widget.show()

    def create_category(self):
        self.create_category_widget = CreateCategoryWidget()
        self.create_category_widget.show()

    def check_categories(self):
        self.check_categories_widget = CheckCategoriesWidget()
        self.initTable()
        self.check_categories_widget.show()

    def check_finished_tasks(self):
        self.check_finished_tasks_widget = CheckFinishedTasksWidget()
        self.initTable()
        self.check_finished_tasks_widget.show()
