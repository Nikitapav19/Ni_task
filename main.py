import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

from mainwindow_ui import MainWindowUi
from mainwindow import MainWindowFunctionality

if __name__ == "__main__":
    """Запуск самого приложения"""
    app = QApplication(sys.argv)
    mw = MainWindowUi()
    mw.show()
    functionality = MainWindowFunctionality(mw)
    app.exec_()
