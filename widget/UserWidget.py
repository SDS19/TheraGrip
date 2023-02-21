import os
import sys
import shutil
from PyQt5.Qt import *

from widget.IOChart import load_chart


def get_user_list():  # list dirs in user dir 
    return os.listdir(os.path.join(os.path.dirname(__file__), 'user'))


class UserBar(QWidget):
    userChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.username = 'demo'

        self.init()
        self.show()

    def init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        """ ********** choose user ********** """

        user_lab = QLabel('Current user: ', self)

        self.user_box = QComboBox(self)
        self.user_box.setFixedWidth(150)
        self.user_box.addItems(get_user_list())  # load [username] from user dir
        self.user_box.currentIndexChanged.connect(self.user_changed_slot)
        self.user_box.setCurrentText('demo')

        layout.addWidget(user_lab, 0, 0)
        layout.addWidget(self.user_box, 0, 1)

        """ ********** create user ********** """

        new_lab = QLabel('Create user: ', self)

        self.new_user = QLineEdit(self)
        self.new_user.setAlignment(Qt.AlignCenter)

        add_btn = QPushButton('Create', self)
        add_btn.setToolTip('Create a new user!')
        add_btn.pressed.connect(self.create_user_slot)

        layout.addWidget(new_lab, 0, 2)
        layout.addWidget(self.new_user, 0, 3)
        layout.addWidget(add_btn, 0, 4)

    def user_changed_slot(self):
        self.username = self.user_box.currentText()
        self.userChanged.emit(self.username)

    """ ******************** create new user ******************** """

    def create_user_slot(self):
        username = self.new_user.text()
        if not len(username) == 0:
            self.mkdir_user(username)
            self.user_box.clear()
            self.user_box.addItems(get_user_list())  # reload
        else:
            QMessageBox.information(self, "Error!", "User cannot be null!")

    def mkdir_user(self, username):
        user_path = os.path.join(os.path.dirname(__file__), 'user', username)  # user dir
        if not os.path.exists(user_path):

            os.mkdir(user_path)  # make user dir
            os.mkdir(os.path.join(user_path, 'log'))  # make log dir
            os.mkdir(os.path.join(user_path, 'log', 'hand'))
            os.mkdir(os.path.join(user_path, 'log', 'arm'))

            demo_config = os.path.join(os.path.dirname(__file__), 'user', 'demo', 'config')  # template config dir
            user_config = os.path.join(user_path, 'config')
            shutil.copytree(demo_config, user_config)  # copy config dir

            QMessageBox.information(self, "Done!", "New user added success under: \n" + user_path)
        else:
            QMessageBox.information(self, "Error!", "This user exists already!")
            print(user_path)


class UserHistory(QWidget):
    def __init__(self, username, obj):
        super().__init__()
        self.username = username
        self.obj = obj

        self.init()
        self.show()

    def init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        label = QLabel('Test History: ', self)

        btn = QPushButton('Open file', self)
        btn.pressed.connect(self.open_file)

        layout.addWidget(label, 0, 0)
        layout.addWidget(btn, 0, 1, 1, 2)

        return layout

    def open_file(self):
        path = os.path.join(os.path.dirname(__file__), 'user', self.username, 'log', self.obj)
        file = QFileDialog(self, "Choose the log file", path, "All(*.*)")
        file.fileSelected.connect(lambda f: load_chart(f))
        file.open()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UserBar()
    sys.exit(app.exec_())