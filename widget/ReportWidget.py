import sys
from PyQt5.Qt import *
from widget.IOChart import *
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


def read_date_range(username, folder):
    file_list = os.listdir(os.path.join(os.path.dirname(__file__), 'user', username, 'log', folder))
    date_list = []
    for filename in file_list:
        file_date = [int(s) for s in filename[0:10].split('-')]
        date_list.append(QDate(file_date[2], file_date[1], file_date[0]))

    print(max(date_list), min(date_list))
    return [min(date_list), max(date_list)]


def load_chart_data_range(date_range, username, folder, param):
    dir_path = os.path.join(os.path.dirname(__file__), 'user', username, 'log', folder)

    from_date = date_range[0]
    to_date = date_range[1]

    # get file list within range
    range_file_list = []
    file_list = os.listdir(dir_path)
    for file in file_list:
        day = int(file[0:2])
        month = int(file[3:5])
        year = int(file[6:10])
        file_date = QDate(year, month, day)
        if file.find(param) != -1 and from_date <= file_date <= to_date:
            range_file_list.append(file)

    y1_max = []
    y2_max = []
    # read data from range_file_list
    for filename in range_file_list:
        y1 = []
        y2 = []
        file = open(os.path.join(dir_path, filename), "r")
        str_lines = file.readlines()
        str_line_1 = str_lines[0].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')
        str_line_2 = str_lines[1].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')
        for s1, s2 in zip(str_line_1, str_line_2):
            y1.append(float(s1))
            y2.append(float(s2))
        file.close()

        y1_max.append(max(to_clean_list(y1)))
        y2_max.append(max(to_clean_list(y2)))

    return [y1_max, y2_max]


class Calendar(QCalendarWidget):
    def __init__(self):
        super().__init__()

        self.from_date = None
        self.to_date = None

        self.highlighter = QTextCharFormat()
        self.highlighter.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlighter.setForeground(self.palette().color(QPalette.HighlightedText))

        self.clicked.connect(self.select_date_range)

    def select_date_range(self, date_value):
        self.highlight_range(QTextCharFormat())
        # hold the shift key to select
        if QApplication.instance().keyboardModifiers() & Qt.ShiftModifier and self.from_date:
            self.to_date = date_value
            self.highlight_range(self.highlighter)
        else:
            self.from_date = date_value
            self.to_date = None

    def highlight_range(self, format):
        if self.from_date and self.to_date:
            d1 = min(self.from_date, self.to_date)
            d2 = max(self.from_date, self.to_date)
            while d2 >= d1:
                self.setDateTextFormat(d1, format)
                d1 = d1.addDays(1)


class PlotCanvas(QWidget):
    def __init__(self, title, x, y1, y2, y_label):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = plt.figure()
        plt.subplot(1, 1, 1)
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel(y_label)
        plt.plot(x, y1, y2)
        plt.grid()

        self.canvas = FigureCanvasQTAgg(self.figure)
        # self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.show()


class HandReport(QWidget):
    def __init__(self):
        super().__init__()
        self.username = 'demo'

        self.list()
        self.init()
        self.show()

    def user_changed_slot(self, username):
        self.username = username
        print("hand report: " + username)
        self.date_layout()

    def list(self):
        self.force_x = []
        self.force_y = []

        self.position_1 = []
        self.position_2 = []

        self.velocity_1 = []
        self.velocity_2 = []

    def init(self):
        self.setWindowTitle('Hand Report')

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addLayout(self.date_layout(), 0, 0, 1, 3)
        self.layout.addLayout(self.chart_layout(self.data_range), 1, 0, 3, 6)
        # self.range_info(layout)
        # self.velocity_layout(layout)

    def date_layout(self):
        self.data_range = read_date_range(self.username, 'hand')
        from_date = self.data_range[0]
        to_date = self.data_range[1]

        layout = QGridLayout()

        self.calendar = Calendar()
        self.calendar.setMinimumDate(from_date)
        self.calendar.setMaximumDate(to_date)

        date_lab = QLabel('Choose date range: ', self)
        self.range_lab = QLabel(from_date.toString('dd.MM.yyyy') + ' ~ ' + to_date.toString('dd.MM.yyyy'), self)
        self.range_lab.setFixedWidth(250)
        self.range_lab.setAlignment(Qt.AlignCenter)

        calendar_btn = QPushButton('Calendar', self)
        calendar_btn.setToolTip('Select the training date range!')
        calendar_btn.pressed.connect(self.show_calendar)
        
        reset_btn = QPushButton('Reset', self)
        reset_btn.pressed.connect(self.load_date_range)

        layout.addWidget(date_lab, 0, 0)
        layout.addWidget(self.range_lab, 0, 1)
        layout.addWidget(calendar_btn, 0, 2)
        layout.addWidget(reset_btn, 0, 3)

        return layout

    def show_calendar(self):
        btn = QPushButton('Confirm')
        btn.clicked.connect(self.set_date_range)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(btn)

        self.dialog = QDialog(self)
        self.dialog.setModal(True)
        self.dialog.setLayout(layout)
        self.dialog.show()
        
    def load_date_range(self):
        self.data_range = read_date_range(self.username, 'hand')
        from_date = self.data_range[0]
        to_date = self.data_range[1]
        
        self.range_lab.setText(from_date.toString('dd.MM.yyyy') + ' ~ ' + to_date.toString('dd.MM.yyyy'), self)
        self.chart_layout()

    def set_date_range(self):
        if self.calendar.from_date and self.calendar.to_date:
            from_date = self.calendar.from_date
            to_date = self.calendar.to_date
            self.range_lab.setText(from_date.toString('dd.MM.yyyy') + ' ~ ' + to_date.toString('dd.MM.yyyy'))
            self.data_range = [from_date, to_date]
            self.layout.addLayout(self.chart_layout(self.data_range), 1, 0, 3, 6)
            self.dialog.close()
        else:
            QMessageBox.information(self, "Error!", "Please choose the date range!")

    def chart_layout(self, data_range):
        layout = QHBoxLayout()

        position_data = load_chart_data_range(data_range, self.username, 'hand', 'position')
        velocity_data = load_chart_data_range(data_range, self.username, 'hand', 'velocity')

        self.position_1 = position_data[0]
        self.position_2 = position_data[1]
        self.velocity_1 = velocity_data[0]
        self.velocity_2 = velocity_data[1]
        x_axis = [i for i in range(len(self.velocity_1))]

        position_chart = PlotCanvas('Position Chart', x_axis, self.position_1, self.position_2, 'position')
        velocity_chart = PlotCanvas('Velocity Chart', x_axis, self.velocity_1, self.velocity_2, 'velocity')

        layout.addWidget(position_chart)
        layout.addWidget(velocity_chart)

        return layout

    """ **********  ********** """

    def range_info(self, layout):
        motor_1 = QLabel('Motor 1', self)
        motor_2 = QLabel('Motor 2', self)
        motor_1.setAlignment(Qt.AlignCenter)
        motor_2.setAlignment(Qt.AlignCenter)

        layout.addWidget(motor_1, 4, 1)
        layout.addWidget(motor_2, 4, 2)

        range_lab = QLabel('max. Range (mm): ', self)

        self.range_val_1 = QLabel('12%', self)
        self.range_val_2 = QLabel('15%', self)
        self.range_val_1.setAlignment(Qt.AlignCenter)
        self.range_val_2.setAlignment(Qt.AlignCenter)

        layout.addWidget(range_lab, 5, 0)
        layout.addWidget(self.range_val_1, 5, 1)
        layout.addWidget(self.range_val_2, 5, 2)

    def velocity_layout(self, layout):
        velo_lab = QLabel('max. Velocity (mm/s): ', self)

        self.velo_val_1 = QLabel('20%', self)
        self.velo_val_2 = QLabel('23%', self)
        self.velo_val_1.setAlignment(Qt.AlignCenter)
        self.velo_val_2.setAlignment(Qt.AlignCenter)

        layout.addWidget(velo_lab, 6, 0)
        layout.addWidget(self.velo_val_1, 6, 1)
        layout.addWidget(self.velo_val_2, 6, 2)


class ArmReport(QWidget):
    def __init__(self):
        super().__init__()
        self.username = 'demo'

        self.force_x = []
        self.force_y = []

        self.init()
        self.show()

    def user_changed_slot(self, username):
        self.username = username
        print("arm report: " + username)
        self.date_layout()

    def init(self):
        self.setWindowTitle('Arm Report')

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addLayout(self.date_layout(), 0, 0, 1, 3)
        self.layout.addLayout(self.chart_layout(self.data_range), 1, 0, 3, 6)
        # self.range_info(layout)
        # self.velocity_layout(layout)

    def date_layout(self):
        self.data_range = read_date_range(self.username, 'arm')
        from_date = self.data_range[0]
        to_date = self.data_range[1]

        layout = QGridLayout()

        self.calendar = Calendar()
        self.calendar.setMinimumDate(from_date)
        self.calendar.setMaximumDate(to_date)

        date_lab = QLabel('Choose date range: ', self)
        self.range_lab = QLabel(from_date.toString('dd.MM.yyyy') + ' ~ ' + to_date.toString('dd.MM.yyyy'), self)
        self.range_lab.setFixedWidth(250)
        self.range_lab.setAlignment(Qt.AlignCenter)

        self.calendar_btn = QPushButton('Calendar', self)
        self.calendar_btn.setToolTip('Select the training date range!')
        self.calendar_btn.pressed.connect(self.show_calendar)

        layout.addWidget(date_lab, 0, 0)
        layout.addWidget(self.range_lab, 0, 1)
        layout.addWidget(self.calendar_btn, 0, 2)

        return layout

    def show_calendar(self):
        btn = QPushButton('Confirm')
        btn.clicked.connect(self.set_date_range)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(btn)

        self.dialog = QDialog(self)
        self.dialog.setModal(True)
        self.dialog.setLayout(layout)
        self.dialog.show()

    def set_date_range(self):
        if self.calendar.from_date and self.calendar.to_date:
            from_date = self.calendar.from_date
            to_date = self.calendar.to_date
            self.range_lab.setText(from_date.toString('dd.MM.yyyy') + ' ~ ' + to_date.toString('dd.MM.yyyy'))
            self.data_range = [from_date, to_date]
            self.layout.addLayout(self.chart_layout(self.data_range), 1, 0, 3, 6)
            self.dialog.close()
        else:
            QMessageBox.information(self, "Error!", "Please choose the date range!")

    def chart_layout(self, data_range):
        layout = QHBoxLayout()

        force_data = load_chart_data_range(data_range, self.username, 'arm', 'force')

        self.force_x = to_force_list(force_data[0])
        self.force_y = to_force_list(force_data[1])
        x_axis = [i for i in range(len(self.force_x))]

        layout.addWidget(PlotCanvas('Force Chart', x_axis, self.force_x, self.force_y, 'force (N)'))

        return layout


if __name__ == '__main__':
    # file_list = os.listdir(os.path.join(os.path.dirname(__file__), 'user', 'demo', 'log', 'arm'))
    # date_range = read_date_range('demo', 'arm')
    # load_chart_data_range(date_range, 'demo', 'arm', 'position')
    # # read_date_range('demo', 'arm')
    app = QApplication(sys.argv)
    win = HandReport()
    sys.exit(app.exec_())