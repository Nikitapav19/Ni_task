from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class MainWindowUi(QMainWindow):
    """Инициализаия основного окна"""
    def __init__(self):
        super().__init__()
        uic.loadUi('interface/mainwindow.ui', self)
        self.initUi()

    def initUi(self):
        self.setWindowTitle('Управление задачами')
        self.setFixedSize(650, 735)
