from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox, qApp
from pf_data import get_driver, get_name_id_pairs, get_attendances_by_subjects
from PyQt5.QtGui import QIcon
import sys


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.__id, self.__pw = '', ''
        self.__data = ()

    def init_ui(self):
        exit_action = QAction(QIcon('./img/quit.png'), 'Quit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Quit application')
        exit_action.triggered.connect(qApp.quit)

        update_action = QAction(QIcon('./img/update.png'), 'Update', self)
        update_action.setShortcut('Ctrl+U')
        update_action.setStatusTip('Update course status')
        update_action.triggered.connect(self.get_data_to_update)

        self.statusBar()

        toolbar = self.addToolBar('ToolBar')
        toolbar.addAction(exit_action)
        toolbar.addAction(update_action)

        self.setWindowTitle('Lecture Checker')
        self.setGeometry(300, 300, 300, 300)
        self.show()

    def get_data_to_update(self):
        if self.__id and self.__pw:
            driver = get_driver()
            self.__data = get_attendances_by_subjects(get_name_id_pairs(self.__id, self.__pw, driver), driver)
        else: QMessageBox.critical(self, 'Missing Information', 'The ID and password\nhave not been entered yet.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
