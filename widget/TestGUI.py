from ArmWidget import *
from HandWidget import *
from UserWidget import UserBar
from PyQt5.QtWebEngineWidgets import QWebEngineView


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TheraGrip")
        self.setGeometry(0, 0, 1800, 720)

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        tab_layout = QVBoxLayout()

        user_bar = UserBar()
        tab_widget = TabWidget()
        user_bar.userChanged.connect(tab_widget.user_changed_slot)

        tab_layout.addWidget(user_bar)
        tab_layout.addWidget(tab_widget)

        layout.addWidget(UnityWidget())
        layout.addLayout(tab_layout)

        self.show()


class TabWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.user_tab = QWidget()
        self.developer_tab = QWidget()
        self.report_tab = QWidget()

        self.addTab(self.user_tab, 'User')
        self.addTab(self.developer_tab, 'Developer')
        self.addTab(self.report_tab, 'Report')

        user_layout = QVBoxLayout()
        self.user_group = UserGroup()
        user_layout.addWidget(self.user_group)
        self.user_tab.setLayout(user_layout)

        dev_layout = QVBoxLayout()
        self.dev_group = DevGroup()
        dev_layout.addWidget(self.dev_group)
        self.developer_tab.setLayout(dev_layout)

        # report_layout = QVBoxLayout()
        # report_layout.addWidget(ReportGroup())
        # self.report_tab.setLayout(report_layout)

    def user_changed_slot(self, username):
        self.user_group.user_change_slot(username)
        self.dev_group.user_change_slot(username)


class UserGroup(QWidget):
    def __init__(self):
        super().__init__()

        self.hand_user = HandUser()
        self.arm_user = ArmUser()

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        hand_box = QGroupBox("Hand")
        hand_box.setCheckable(True)
        hand_box.setLayout(self.hand_layout())
        layout.addWidget(hand_box)

        arm_box = QGroupBox("Arm")
        arm_box.setCheckable(True)
        arm_box.setLayout(self.arm_layout())
        layout.addWidget(arm_box)

        self.show()

    def hand_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.hand_user)
        return layout

    def arm_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.arm_user)
        return layout

    def user_change_slot(self, username):
        print("user group: " + username)
        self.hand_user.user_changed_slot(username)
        self.arm_user.user_changed_slot(username)


class DevGroup(QWidget):
    def __init__(self):
        super().__init__()
        self.hand_dev = HandDev()
        self.arm_dev = ArmDev()

        layout = QVBoxLayout()
        self.setLayout(layout)

        hand_box = QGroupBox("Hand")
        hand_box.setCheckable(True)
        hand_box.setLayout(self.hand_layout())
        layout.addWidget(hand_box)

        arm_box = QGroupBox("Arm")
        arm_box.setCheckable(True)
        arm_box.setLayout(self.arm_layout())
        layout.addWidget(arm_box)

        self.show()

    def hand_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.hand_dev)
        return layout

    def arm_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.arm_dev)
        return layout

    def user_change_slot(self, username):
        self.hand_dev.user_changed_slot(username)
        self.arm_dev.user_changed_slot(username)


class ReportGroup(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        hand_box = QGroupBox("Hand")
        hand_box.setCheckable(True)
        hand_box.setLayout(self.hand_layout())
        layout.addWidget(hand_box)

        arm_box = QGroupBox("Arm")
        arm_box.setCheckable(True)
        arm_box.setLayout(self.arm_layout())
        layout.addWidget(arm_box)

        self.show()

    def hand_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(HandReport())
        return layout

    def arm_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(ArmReport())
        return layout


class UnityWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1280, 720)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.view = QWebEngineView()
        self.view.load(QUrl("http://127.0.0.1:5500/index.html"))
        layout.addWidget(self.view)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())