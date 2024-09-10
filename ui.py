from statistic import pass_rate_of_total, pass_rate_by_subjects, get_untaken_lectures
from pf_data import get_driver, get_name_id_pairs, get_attendances_by_subjects
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
import sys


class InputIDPwDialog(QDialog):
    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)

        self.__fst = QLineEdit(self)
        self.__snd = QLineEdit(self)
        self.__snd.setEchoMode(QLineEdit.Password)
        input_bx = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        f_layout = QFormLayout(self)
        f_layout.addRow('ID: ', self.__fst)
        f_layout.addRow('PW: ', self.__snd)
        f_layout.addWidget(input_bx)

        input_bx.accepted.connect(self.accept)
        input_bx.rejected.connect(self.reject)

    def get_inputs(self):
        return self.__fst.text(), self.__snd.text()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__id, self.__pw = '', ''
        self.__data = ()
        self.init_ui()

    def init_ui(self):
        exit_action = QAction(QIcon('./img/quit.png'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('프로그램을 종료합니다')
        exit_action.triggered.connect(qApp.quit)

        update_action = QAction(QIcon('./img/update.png'), 'Update', self)
        update_action.setShortcut('Ctrl+U')
        update_action.setStatusTip('수강 내역을 갱신합니다')
        update_action.triggered.connect(self.get_data_to_update)

        self.statusBar()

        toolbar = self.addToolBar('ToolBar')
        toolbar.addAction(exit_action)
        toolbar.addAction(update_action)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab_of_pass_rate(), '수강률')
        self.tabs.addTab(self.tab_of_untaken_lecture(), '미수강 강의')

        self.id_input = QLineEdit(self)
        self.pw_input = QLineEdit(self)
        self.submit = QPushButton('실행', self)
        self.show_whether_submitted = QRadioButton('ID/PW 설정됨', self)

        self.id_input.setStatusTip('블랙보드의 아이디를 입력합니다')
        self.pw_input.setStatusTip('블랙보드의 비밀번호를 입력합니다')
        self.submit.setStatusTip('아이디와 비밀번호를 이용해 수강 내역을 조회합니다')
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.show_whether_submitted.setEnabled(False)
        self.submit.clicked.connect(self.set_and_run)

        login_box = QHBoxLayout()

        login_box.addWidget(self.show_whether_submitted)
        login_box.addWidget(QLabel('ID : '))
        login_box.addWidget(self.id_input)
        login_box.addWidget(QLabel('PW : '))
        login_box.addWidget(self.pw_input)
        login_box.addWidget(self.submit)

        vbox = QVBoxLayout()
        vbox.addLayout(login_box)
        vbox.addWidget(self.tabs)

        widget = QWidget()

        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setWindowTitle('Lecture Checker')
        self.resize(525, 400)
        self.set_center()
        self.show()

    def set_center(self):
        geometry = self.frameGeometry()
        ctr_point = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(ctr_point)
        self.move(geometry.topLeft())

    def set_login_info(self):
        self.__id = self.id_input.text()
        self.__pw = self.pw_input.text()

        self.show_whether_submitted.setChecked(True)
        self.id_input.setText(None)
        self.pw_input.setText(None)

    def set_and_run(self):
        self.set_login_info()
        self.get_data_to_update()

    def get_data_to_update(self):
        if self.__id and self.__pw:
            driver = get_driver()
            self.__data = get_attendances_by_subjects(get_name_id_pairs(self.__id, self.__pw, driver), driver)

            self.tabs.clear()
            self.tabs.addTab(self.tab_of_pass_rate(), '수강률')
            self.tabs.addTab(self.tab_of_untaken_lecture(), '미수강 강의')
        else:
            QMessageBox.critical(self, '정보 누락', '아이디 또는 비밀번호가 존재하지 않습니다')

    def abstacted_tab(self, widget_fn):
        v_box1 = QVBoxLayout()
        v_box2 = QVBoxLayout()

        if not (does_exist := bool(self.__data)):
            no_data = QLabel('수집된 정보가 존재하지 않습니다')
            h_box = QHBoxLayout()
            h_box.addStretch(1)
            h_box.addWidget(no_data)
            h_box.addStretch(1)
            v_box1.addStretch(1)
            v_box1.addLayout(h_box)
            v_box1.addStretch(1)
        else:
            v_box2.addWidget(widget_fn())

        tab = QWidget()
        tab.setLayout(v_box2 if does_exist else v_box1)
        return tab

    def tab_of_pass_rate(self):

        def table():
            total = pass_rate_of_total(self.__data)
            subjects = pass_rate_by_subjects(self.__data)

            pass_rate_table = QTableWidget()
            pass_rate_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            pass_rate_table.setRowCount(len(subjects) + 1)
            pass_rate_table.setColumnCount(4)

            header = pass_rate_table.horizontalHeader()
            for i in range(4):
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents if i != 0 else QtWidgets.QHeaderView.Stretch)

            pass_rate_table.setHorizontalHeaderLabels(('과목명', '   총 강의 수   ', '   수강 강의 수   ', '   수강률   '))
            for i, (k, v) in enumerate(({'total': total} | subjects).items()):
                for j, u in enumerate((k,) + v):
                    item = QTableWidgetItem((f'{u:0.3f}' if type(u) is float else f'{u}') + ('' if j != 3 else ' %'))
                    if j != 0: item.setTextAlignment(2)
                    pass_rate_table.setItem(i, j, item)

            return pass_rate_table

        return self.abstacted_tab(table)

    def tab_of_untaken_lecture(self):

        def table():
            utk_lecture = get_untaken_lectures(self.__data)

            utk_lec_table = QTableWidget()
            utk_lec_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            utk_lec_table.setRowCount(len(utk_lecture))
            utk_lec_table.setColumnCount(3)

            header = utk_lec_table.horizontalHeader()
            for i in range(3):
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents if i == 2 else QtWidgets.QHeaderView.Stretch)

            utk_lec_table.setHorizontalHeaderLabels(('과목명', '강의명', '마감 날짜 & 시간'))

            for i, v in enumerate(utk_lecture):
                for j, u in enumerate(v):
                    item = QTableWidgetItem('{}'.format(u if type(u) is str else u.strftime('%Y.%m.%d %H:%M')))
                    utk_lec_table.setItem(i, j, item)

            return utk_lec_table

        return self.abstacted_tab(table)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
