import datetime
import sqlite3

from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate

from PyQt5.QtWidgets import QWidget, QTableWidgetItem


class CreateTaskWidget(QWidget):
    """
    Виджет создания задачи
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('interface/create_task.ui',
                   self)
        self.initUi()

    def initUi(self):
        """
        Инициализация всего интерфейса в окне
        Все init в этом классе - разбитые на части инициализации для более удобного пользования
        """
        self.setWindowTitle('Создание задачи')
        self.error_message.hide()
        self.task_create_button.show()
        self.setFixedSize(464, 464)
        self.task_create_button.setText('Создать задачу')

        self.initDate()
        self.initPriority()
        self.initCategories()
        self.task_cancel_button.clicked.connect(self.clicked_cancel_button)
        self.task_create_button.clicked.connect(self.clicked_create_button)

    def clicked_cancel_button(self):
        self.close()

    def initDate(self):
        self.task_date.setCalendarPopup(True)
        self.task_date.setDate(QDate.currentDate())

    def initPriority(self):
        priorities = ['Низкий', 'Средний', 'Высокий']
        for element in priorities:
            self.task_priority.addItem(element)

    def initCategories(self):
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        result = cur.execute('SELECT category_name FROM Categories').fetchall()
        for row in result:
            self.task_category.addItem(row[0])

    def clicked_create_button(self):
        """
        Пользователь нажал на кнопку 'Создать задачу'
        Создаем задачу или выводим ошибку в зависимости от правильности введенных данных
        """
        if not self.task_title.text():
            self.error_message.show()
            self.error_message.setText('Неверные данные')
        else:
            con = sqlite3.connect('database/database.sqlite')
            cur = con.cursor()
            date = self.task_date.date()
            selected_date = date.toString('dd-MM-yyyy')
            query = '''INSERT INTO Tasks(title, deadline, priority, categories, description, status, start_time) 
                       VALUES(?, ?, ?, ?, ?, ?, ?)'''
            text = self.task_category.currentText()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            category_id = cur.execute('SELECT category_id FROM Categories WHERE category_name = ?',
                                      (text,)).fetchone()[0]
            values = (self.task_title.text(), selected_date, self.task_priority.currentText(),
                      category_id, self.task_description.toPlainText(), 0, current_time)
            self.error_message.show()
            try:
                cur.execute(query, values)
                con.commit()
                self.error_message.setText('Данные успешно добавлены')
            except sqlite3.Error:
                self.error_message.setText('Ошибка при добавлении данных')
            con.close()
            self.clear_lines()

    def clear_lines(self):
        """
        В случае удачного создания задачи, все поля очищаются
        """
        self.task_title.clear()
        self.task_date.setDate(QDate.currentDate())
        self.task_description.clear()


class CreateCategoryWidget(QWidget):
    """
    Виджет создания категории
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('interface/create_category.ui',
                   self)
        self.initUi()

    def initUi(self):
        """
        Инициализация интерфейса
        """
        self.setFixedSize(400, 93)
        self.label_message.hide()
        self.setWindowTitle("Создание категории")
        self.create_category_button.clicked.connect(self.create_category)
        self.category_cancel_button.clicked.connect(self.clicked_category_cancel)

    def clicked_category_cancel(self):
        self.close()

    def create_category(self):
        """
        Пользователь нажал на создание категории
        Функция создаст категорию с названием, которое было указано пользователем
        """
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        category = self.category_title.text()
        if 0 < len(category) < 30:
            cur.execute('''INSERT INTO Categories(category_name) VALUES(?)''',
                        (category,))
            self.label_message.show()
            self.label_message.setText('Категория успешно создана')
            self.category_title.clear()
        elif len(category) == 0:
            self.label_message.show()
            self.label_message.setText('Ошибка! Вы не ввели название')
        else:
            self.label_message.show()
            self.label_message.setText('Ошибка! Длина более 30 символов')
        con.commit()


class CheckCategoriesWidget(QWidget):
    """
    Виджет с уже созданными категориями
    """
    def __init__(self):
        super().__init__()
        self.dc = None
        uic.loadUi('interface/check_categories.ui',
                   self)
        self.initUi()

    def initUi(self):
        """
        Инициализация интерфейса
        """
        self.error_message.hide()
        self.setFixedSize(400, 300)
        self.setWindowTitle('Список категорий')
        self.back_button.clicked.connect(self.clicked_back_button)
        self.initTable()
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_category)

    def clicked_back_button(self):
        self.close()

    def delete_category(self):
        """
        Удаление произойдет только в случае, если задачи в выбранной категории отсутствуют
        иначе программа выведет ошибку на экран
        """
        selected_category = [item.text() for item in self.tableWidget.selectedItems()]
        if selected_category:
            self.error_message.hide()
            con = sqlite3.connect('database/database.sqlite')
            cur = con.cursor()
            text = cur.execute('SELECT category_name FROM Categories '
                               'WHERE category_name = ?',
                               (str(selected_category[0]),)).fetchall()[0][0]
            self.dc = DeleteConfirmation(text, 'category')
            self.dc.show()
            self.close()
        else:
            self.error_message.show()
            self.delete_button.setEnabled(False)

    def selected_cell(self):
        self.delete_button.setEnabled(True)

    def initTable(self):
        """
        Инициализирует таблицу с категориями, которые уже находятся в БД
        """
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        result = cur.execute('SELECT category_name FROM Categories').fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('Название'))
        self.tableWidget.setColumnWidth(0, 400)
        for i, row in enumerate(result):
            item = QTableWidgetItem(row[0])
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.tableWidget.setItem(i, 0, item)
        self.tableWidget.cellClicked.connect(self.selected_cell)


class CheckFinishedTasksWidget(QWidget):
    """
    Виджет с выполненными задачами
    """
    def __init__(self):
        super().__init__()
        self.dc = None
        uic.loadUi('interface/check_finished_tasks.ui',
                   self)
        self.initUi()

    def initUi(self):
        """
        Инициализация
        """
        self.setFixedSize(596, 556)
        self.setWindowTitle('Завершенные задачи')
        self.error_message.hide()
        self.back_button.clicked.connect(self.clicked_back_button)
        self.delete_button.clicked.connect(self.delete_task)
        self.delete_button.setEnabled(False)

        self.initTable()

    def clicked_back_button(self):
        self.close()

    def selected_cell(self, row: int, column: int):
        """
        Проверяет выбранную ячейку
        """
        if column == 0:
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)

    def delete_task(self):
        """
        Находит нужные значение, которые выбрал пользователь для удаления
        """
        self.error_message.hide()
        items = self.tableWidget.selectedItems()
        selected_task = [item.text() for item in items]
        if selected_task:
            con = sqlite3.connect('database/database.sqlite')
            cur = con.cursor()
            text = cur.execute('SELECT title FROM Tasks WHERE title = ?',
                               (selected_task[0], )).fetchall()[0][0]
            self.dc = DeleteConfirmation(text, 'task')  # Переход к классу об удалении
            self.dc.show()
            self.close()
        else:
            self.delete_button.setEnabled(False)  # Выводит ошибку об отсутствии выбранной задачи
            self.error_message.show()

    def initTable(self):
        """
        Инициализирует таблицу с завершенными пользователем задачами
        Выбирает только те, у которых status=1
        """
        horizontal_headers = ['Название', 'Категория', 'Сроки', 'Приоритет', 'Затраченное время']
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        result = cur.execute('''SELECT Tasks.title, Categories.category_name,
                                Tasks.deadline, Tasks.priority, Tasks.time_spent FROM Tasks
                                INNER JOIN Categories ON Tasks.categories = Categories.category_id
                                WHERE Tasks.status = 1''').fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setColumnWidth(0, 124)
        self.tableWidget.setColumnWidth(4, 130)
        for i, element in enumerate(horizontal_headers):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(element))
        for i, elements in enumerate(result):
            for j in range(len(elements)):
                item = QTableWidgetItem(elements[j])
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Запрещает редактировать значения
                self.tableWidget.setItem(i, j, item)
        self.tableWidget.cellClicked.connect(self.selected_cell)


class CheckInfoOfTask(QWidget):
    """
    Информация о выбранной пользователем задаче
    """
    def __init__(self, selected_name=None):
        super().__init__()
        uic.loadUi('interface/check_info.ui',
                   self)
        self.selected_name = selected_name
        self.initUi()

    def initUi(self):
        """
        Инициализация
        """
        self.setWindowTitle('Информация')
        self.setFixedSize(377, 435)

        self.title_line.setReadOnly(True)
        self.deadline_line.setReadOnly(True)
        self.priority_line.setReadOnly(True)
        self.category_line.setReadOnly(True)
        self.task_description.setReadOnly(True)
        self.back_button.clicked.connect(self.back_button_clicked)

        if self.selected_name:
            self.initLines()  # Выполняет полную инициализацию всех значений
        else:
            self.task_description.setPlainText('Вернитесь и выберите задачу')  # Выдает ошибку

    def initLines(self):
        """
        Сработает только в случае, если пользователь выбрал название задачи в tableWidget именно из первой колонки
        """
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        result = cur.execute('SELECT Tasks.title, Tasks.deadline, Tasks.priority, '
                             'Categories.category_name, Tasks.description '
                             'FROM Tasks, Categories '
                             'WHERE Tasks.title = ?',
                             (self.selected_name, )).fetchall()
        self.title_line.setText(result[0][0])
        self.deadline_line.setText(result[0][1])
        self.priority_line.setText(result[0][2])
        self.category_line.setText(result[0][3])
        self.task_description.setPlainText(result[0][4])

    def back_button_clicked(self):
        self.close()


class DeleteConfirmation(QWidget):
    """
    Диалоговое окно о подтверждении удаления выбранной категории/задачи
    Если text = category - значит пользователь удаляет категорию
    Если text = task - значит пользователь удаляет задачу
    """
    def __init__(self, text, style):
        super().__init__()
        uic.loadUi('interface/delete_confirmation.ui',
                   self)
        self.text = text
        self.style = style
        self.initUi()

    def initUi(self):
        """
        Инициализация
        """
        self.error_message.hide()
        self.setFixedSize(479, 115)
        self.setWindowTitle('Подтверждение')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        if self.style == 'category':
            self.label.setText(f'Вы уверены, что хотите удалить выбранную категорию?'
                               f'\nНазвание категории: {self.text}')
            self.decline_button.clicked.connect(self.category_decline_button_clicked)
            self.confirm_button.clicked.connect(self.category_confirm_button_clicked)
        elif self.style == 'task':
            self.label.setText('Вы уверены, что хотите удалить выбранную задачу?'
                               f'\nНазвание задачи: {self.text}')
            self.decline_button.clicked.connect(self.task_decline_button_clicked)
            self.confirm_button.clicked.connect(self.task_confirm_button_clicked)

    def category_decline_button_clicked(self):
        self.close()

    def category_confirm_button_clicked(self):
        """
        Пользователь нажал на подтверждение
        функция удаляет выбранную задачу/категорию
        """
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        used_categories = cur.execute(
            'SELECT Tasks.title FROM Categories JOIN Tasks ON Categories.category_id = Tasks.categories '
            'WHERE Categories.category_name = ?', (self.text,)).fetchall()
        if len(used_categories) == 0:
            cur.execute('DELETE FROM Categories WHERE category_name = ?',
                        (self.text,))
            con.commit()
            self.close()
        else:
            self.error_message.show()

    def task_decline_button_clicked(self):
        self.close()

    def task_confirm_button_clicked(self):
        con = sqlite3.connect('database/database.sqlite')
        cur = con.cursor()
        cur.execute('DELETE FROM Tasks WHERE title = ?',
                    (self.text, ))
        con.commit()
        self.close()
