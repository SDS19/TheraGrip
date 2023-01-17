import sys
from PyQt5.Qt import *
from widget.ArmWorker import *
from widget.UserWidget import UserHistory

test = True


class ArmUser(QWidget):
    if test:
        def __init__(self):
            super().__init__()
            self.username = 'demo'

            self.init()
            self.show()
            print("test mode")
    else:
        def __init__(self, x_axis, y_axis):
            super().__init__()
            self.username = 'demo'

            self.x_axis = x_axis
            self.y_axis = y_axis

            self.list()
            self.init()
            self.show()

    def user_changed_slot(self, username):
        self.username = username
        self.user_history_widget.username = username
        print("arm user: " + username)

    def list(self):  # temporarily save data to memory
        self.force_x = []
        self.force_y = []

        self.position_x = []
        self.position_y = []

        self.velocity_x = []
        self.velocity_y = []

    def init(self):
        self.setWindowIcon(QIcon('icon/arm.PNG'))
        self.setWindowTitle('Arm User')

        layout = QVBoxLayout()
        self.setLayout(layout)

        task_group = QGroupBox('Task')
        info_group = QGroupBox('Info')
        train_group = QGroupBox('Setting')

        layout.addWidget(task_group)
        layout.addWidget(info_group)
        layout.addWidget(train_group)

        task_group.setLayout(self.task_layout())
        info_group.setLayout(self.info_layout())
        train_group.setLayout(self.setting_layout())

    """ ******************** task widget ******************** """

    def task_layout(self):
        layout = QGridLayout()
        layout.addWidget(self.task_button('Task 1'), 0, 0)
        layout.addWidget(self.task_button('Task 2'), 0, 1)
        layout.addWidget(self.task_button('Task 3'), 0, 2)
        layout.addWidget(self.task_button('Task 4'), 1, 0)
        layout.addWidget(self.task_button('Task 5'), 1, 1)
        layout.addWidget(self.task_button('Task 6'), 1, 2)
        return layout

    def task_button(self, name):
        config = read_config(name)
        btn = QPushButton(name)
        btn.clicked.connect(lambda: self.start(config[0]+', '+config[1], config[2]+', '+config[3], config[4], config[5]))
        return btn

    def start(self, point_1, point_2, velocity, times):
        self.real_time_slot()

        p1 = parse_to_list(point_1)
        p2 = parse_to_list(point_2)
        
        self.list()
        self.move_worker = ArmMoveThread(self.x_axis, self.y_axis, p1, p2, velocity, times)
        self.move_worker.finish.connect(self.save_record_index)
        self.move_worker.start()
            
    def save_record_index(self):  # finish
        self.index = len(self.force_x)

    def real_time_slot(self):
        self.v_btn.setEnabled(True)
        self.p_btn.setEnabled(True)
        self.f_btn.setEnabled(True)

        self.info_worker = ArmInfoThread(self.x_axis, self.y_axis)
        self.info_worker.update.connect(self.info_update_event)
        self.info_worker.start()

    def info_update_event(self, data):  # finish
        self.force_x.append(data[0][0])
        self.position_x.append(data[0][1])
        self.velocity_x.append(data[0][2])

        self.force_y.append(data[1][0])
        self.position_y.append(data[1][1])
        self.velocity_y.append(data[1][2])

        self.f_x.setText(str(data[0][0]))
        self.p_x.setText(str(data[0][1]))
        self.v_x.setText(str(data[0][2]))

        self.f_y.setText(str(data[1][0]))
        self.p_y.setText(str(data[1][1]))
        self.v_y.setText(str(data[1][2]))

    """ ****************************** info widget ****************************** """

    def info_layout(self):
        layout = QGridLayout()
        self.info_column(layout)
        self.velocity_info(layout)
        self.position_info(layout)
        self.force_info(layout)
        return layout

    def info_column(self, layout):  # column name: X and Y
        x_lab = QLabel('X', self)
        y_lab = QLabel('Y', self)
        x_lab.setAlignment(Qt.AlignCenter)
        y_lab.setAlignment(Qt.AlignCenter)
        layout.addWidget(x_lab, 0, 1)
        layout.addWidget(y_lab, 0, 2)

    ''' finish ********** velocity info ********** '''

    def velocity_info(self, layout):
        v_lab = QLabel('real-time velocity (mm/s): ', self)

        self.v_x = QLabel('0', self)
        self.v_y = QLabel('0', self)
        self.v_x.setFixedWidth(110)
        self.v_y.setFixedWidth(110)
        self.v_x.setAlignment(Qt.AlignCenter)
        self.v_y.setAlignment(Qt.AlignCenter)

        self.v_btn = QPushButton('Chart', self)
        self.v_btn.setEnabled(False)
        self.v_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.velocity_x[0:self.index]), to_clean_list(self.velocity_y[0:self.index]), "X Axis: Velocity record", "Y Axis: Velocity record", "velocity (mm/s)"))

        layout.addWidget(v_lab, 1, 0)
        layout.addWidget(self.v_x, 1, 1)
        layout.addWidget(self.v_y, 1, 2)
        layout.addWidget(self.v_btn, 1, 3)

    ''' finish ********** position info ********** '''

    def position_info(self, layout):
        p_lab = QLabel('real-time position (mm): ', self)

        self.p_x = QLabel('0', self)
        self.p_y = QLabel('0', self)
        self.p_x.setAlignment(Qt.AlignCenter)
        self.p_y.setAlignment(Qt.AlignCenter)

        self.p_btn = QPushButton('Chart', self)
        self.p_btn.setEnabled(False)
        self.p_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.position_x[0:self.index]), to_clean_list(self.position_y[0:self.index]), "X Axis: Position record", "Y Axis: Position record", "position (mm)"))

        layout.addWidget(p_lab, 2, 0)
        layout.addWidget(self.p_x, 2, 1)
        layout.addWidget(self.p_y, 2, 2)
        layout.addWidget(self.p_btn, 2, 3)

    ''' ********** force info ********** '''

    def force_info(self, layout):  # finish
        f_lab = QLabel('real-time force (N): ', self)

        self.f_x = QLabel('0', self)
        self.f_y = QLabel('0', self)
        self.f_x.setAlignment(Qt.AlignCenter)
        self.f_y.setAlignment(Qt.AlignCenter)

        self.f_btn = QPushButton('Chart', self)
        self.f_btn.setEnabled(False)
        self.f_btn.pressed.connect(lambda: triple_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.force_x[0:self.index]), to_clean_list(self.force_y[0:self.index]), "X Axis: component force", "Y Axis: component force", "resultant force", "force (N)"))

        layout.addWidget(f_lab, 3, 0)
        layout.addWidget(self.f_x, 3, 1)
        layout.addWidget(self.f_y, 3, 2)
        layout.addWidget(self.f_btn, 3, 3)

    """ ****************************** Button Widget ****************************** """

    def setting_layout(self):
        layout = QVBoxLayout()
        layout.addLayout(self.button_bar())
        self.user_history_widget = UserHistory(self.username, 'arm')
        layout.addWidget(self.user_history_widget)
        return layout

    def button_bar(self):
        layout = QGridLayout()

        homing_btn = QPushButton('Homing', self)
        homing_btn.setToolTip('Homing the X and Y axes motor to (350, 250)!')
        homing_btn.pressed.connect(self.homing)

        reset_btn = QPushButton('Reset', self)
        reset_btn.setToolTip('Reset motor error and data record!')
        reset_btn.pressed.connect(self.reset)

        stop_btn = QPushButton('Stop', self)
        stop_btn.setToolTip('Stop the current movement!')
        stop_btn.pressed.connect(self.stop)

        save_btn = QPushButton('Save', self)
        save_btn.setToolTip('Save real-time data record!')
        save_btn.pressed.connect(lambda: self.save(True))

        layout.addWidget(homing_btn, 0, 0)
        layout.addWidget(reset_btn, 0, 1)
        layout.addWidget(stop_btn, 0, 2)
        layout.addWidget(save_btn, 0, 3)

        return layout

    def homing(self):  # finish
        self.homing_worker = ArmHomingThread(self.x_axis, self.y_axis)
        self.homing_worker.start()

    def reset(self):  # finish
        self.list()
        self.x_axis.reset_error()
        self.y_axis.reset_error()
        QMessageBox.information(self, "Done!", "Reset error success!")

    def stop(self):  # finish
        self.stop_worker = ArmStopThread(self.x_axis, self.y_axis)
        self.stop_worker.start()

    def save(self, flag):
        force = 'force' if flag else 'force(no_load)'
         
        write_user_log(self.username, 'arm', 'position', self.position_x[0:self.index])
        write_user_log(self.username, 'arm', 'position', '\n' + str(self.position_y[0:self.index]))

        write_user_log(self.username, 'arm', 'velocity', self.velocity_x[0:self.index])
        write_user_log(self.username, 'arm', 'velocity', '\n' + str(self.velocity_y[0:self.index]))
        
        write_user_log(self.username, 'arm', force, self.force_x[0:self.index])
        write_user_log(self.username, 'arm', force, '\n' + str(self.force_y[0:self.index]))

        QMessageBox.information(self, "Done!", "Arm test record saved success!")


class ArmDev(QWidget):
    if test:
        def __init__(self):
            super().__init__()
            self.init()
            self.show()
            print("test mode")
    else:
        def __init__(self, x_axis, y_axis):
            super().__init__()
            self.username = 'demo'

            self.x_axis = x_axis
            self.y_axis = y_axis

            self.list()
            self.init()
            self.show()

    def user_changed_slot(self, username):
        print("arm dev: " + username)

    def list(self):
        self.current_x = []
        self.current_y = []

        self.position_x = []
        self.position_y = []

        self.velocity_x = []
        self.velocity_y = []

    def init(self):
        self.setWindowIcon(QIcon('icon/arm.PNG'))
        self.setWindowTitle('Arm Dev')

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addLayout(self.column_layout(), 0, 0)

        for i in range(6):
            config = read_config('Task ' + str(i + 1))
            layout.addLayout(self.task_layout('Task ' + str(i + 1), config[0] + ', ' + config[1], config[2] + ', ' + config[3], config[4], config[5]), i + 1, 0)

        layout.addLayout(self.info(), 8, 0)
        layout.addLayout(self.button_bar(), 9, 0)

    """ finish ******************** column widget ******************** """

    def column_layout(self):
        layout = QGridLayout()

        space = QLabel(self)
        space.setFixedWidth(50)

        start = QLabel('start (x mm, y mm)', self)
        start.setFixedWidth(120)
        start.setAlignment(Qt.AlignCenter)

        end = QLabel('end (x mm, y mm)', self)
        end.setFixedWidth(120)
        end.setAlignment(Qt.AlignCenter)

        velocity = QLabel('velocity', self)
        velocity.setFixedWidth(50)
        velocity.setAlignment(Qt.AlignCenter)

        times = QLabel('loop', self)
        times.setFixedWidth(50)
        times.setAlignment(Qt.AlignCenter)

        self.stop_btn = QPushButton("stop", self)
        self.stop_btn.setEnabled(False)
        self.stop_btn.pressed.connect(self.stop)

        layout.addWidget(space, 0, 0)
        layout.addWidget(start, 0, 1)
        layout.addWidget(end, 0, 2)
        layout.addWidget(velocity, 0, 3)
        layout.addWidget(times, 0, 4)
        layout.addWidget(self.stop_btn, 0, 5)

        return layout

    def stop(self):
        self.worker = ArmStopThread(self.x_axis, self.y_axis)
        self.worker.start()

    """ finish ******************** task ******************** """

    def task_layout(self, name, start, end, velocity, times):
        layout = QGridLayout()

        lab = QLabel(name, self)
        lab.setFixedWidth(50)

        start_val = QLineEdit(start, self)
        start_val.setFixedWidth(120)
        start_val.setAlignment(Qt.AlignCenter)

        end_val = QLineEdit(end, self)
        end_val.setFixedWidth(120)
        end_val.setAlignment(Qt.AlignCenter)

        velocity_val = QLineEdit(velocity, self)
        velocity_val.setFixedWidth(50)
        velocity_val.setAlignment(Qt.AlignCenter)

        times_val = QLineEdit(times, self)
        times_val.setFixedWidth(50)
        times_val.setAlignment(Qt.AlignCenter)

        btn = QPushButton("start", self)
        btn.pressed.connect(lambda: self.start(name, start_val.text(), end_val.text(), velocity_val.text(), times_val.text()))

        layout.addWidget(lab, 0, 0)
        layout.addWidget(start_val, 0, 1)
        layout.addWidget(end_val, 0, 2)
        layout.addWidget(velocity_val, 0, 3)
        layout.addWidget(times_val, 0, 4)
        layout.addWidget(btn, 0, 5)

        return layout

    def start(self, name, point_1, point_2, velocity, times):
        self.stop_btn.setEnabled(True)
        
        self.real_time_slot()

        p1 = parse_to_list(point_1)
        p2 = parse_to_list(point_2)

        if len(p1) == 2 and len(p2) == 2:
            write_config(name, [p1, p2, velocity, times])
            self.list()  # clear old record
            self.worker = ArmMoveThread(self.x_axis, self.y_axis, p1, p2, velocity, times)
            self.worker.finish.connect(self.save_record_index)
            self.worker.start()
        else:
            QMessageBox.information(self, "Error!", "Please enter correct range value: (0~350), (0~250)")

    def save_record_index(self):  # finish
        self.index = len(self.current_x)

    """ finish ****************************** info widget ****************************** """

    def info(self):
        layout = QGridLayout()
        self.info_column(layout)
        self.force_info(layout)
        self.velocity_info(layout)
        self.position_info(layout)
        return layout

    def info_column(self, layout):
        x_lab = QLabel('X', self)
        y_lab = QLabel('Y', self)
        x_lab.setAlignment(Qt.AlignCenter)
        y_lab.setAlignment(Qt.AlignCenter)

        layout.addWidget(x_lab, 0, 1)
        layout.addWidget(y_lab, 0, 2)

    """ finish ******************** velocity widget ******************** """

    def velocity_info(self, layout):
        v_lab = QLabel('real-time velocity (mm/s): ', self)

        self.v_x = QLabel('0', self)
        self.v_y = QLabel('0', self)
        self.v_x.setAlignment(Qt.AlignCenter)
        self.v_y.setAlignment(Qt.AlignCenter)

        self.v_btn = QPushButton('Chart', self)
        self.v_btn.setFixedWidth(90)
        self.v_btn.setEnabled(False)
        self.v_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.velocity_x[0:self.index]), to_clean_list(self.velocity_y[0:self.index]), "X Axis: Velocity record", "Y Axis: Velocity record", "velocity (mm/s)"))

        layout.addWidget(v_lab, 1, 0)
        layout.addWidget(self.v_x, 1, 1)
        layout.addWidget(self.v_y, 1, 2)
        layout.addWidget(self.v_btn, 1, 3)

    """ finish ******************** position widget ******************** """

    def position_info(self, layout):
        p_lab = QLabel('real-time position (mm): ', self)

        self.p_x = QLabel('0', self)
        self.p_y = QLabel('0', self)
        self.p_x.setAlignment(Qt.AlignCenter)
        self.p_y.setAlignment(Qt.AlignCenter)

        self.p_btn = QPushButton('Chart', self)
        self.p_btn.setFixedWidth(90)
        self.p_btn.setEnabled(False)
        self.p_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.position_x[0:self.index]), to_clean_list(self.position_y[0:self.index]), "X Axis: Position record", "Y Axis: Position record", "position (mm)"))

        layout.addWidget(p_lab, 2, 0)
        layout.addWidget(self.p_x, 2, 1)
        layout.addWidget(self.p_y, 2, 2)
        layout.addWidget(self.p_btn, 2, 3)        

    """ finish ******************** force widget ******************** """

    def force_info(self, layout):
        f_lab = QLabel('real-time force (N): ', self)

        self.f_x = QLabel('0', self)
        self.f_y = QLabel('0', self)
        self.f_x.setAlignment(Qt.AlignCenter)
        self.f_y.setAlignment(Qt.AlignCenter)

        self.f_btn = QPushButton('Chart', self)
        self.f_btn.setFixedWidth(90)
        self.f_btn.setEnabled(False)
        self.f_btn.pressed.connect(lambda: triple_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_force_list(self.current_x[0:self.index]), to_force_list(self.current_y[0:self.index]), "X Axis: component force", "Y Axis: component force", "resultant force", "force (N)"))

        layout.addWidget(f_lab, 3, 0)
        layout.addWidget(self.f_x, 3, 1)
        layout.addWidget(self.f_y, 3, 2)
        layout.addWidget(self.f_btn, 3, 3)

    """ finish ******************** homing widget ******************** """

    def button_bar(self):
        layout = QGridLayout()

        homing_btn = QPushButton('Homing', self)
        homing_btn.setToolTip('Homing the X and Y axes motor to (350, 250)!')
        homing_btn.pressed.connect(self.homing)

        reset_btn = QPushButton('Reset', self)
        reset_btn.setToolTip('Reset motor error and data record!')
        reset_btn.pressed.connect(self.reset)

        update_btn = QPushButton('Real-Time(omit)', self)
        update_btn.setToolTip('Display real-time data!')
        update_btn.pressed.connect(self.real_time_slot)

        save_btn = QPushButton('Save', self)
        save_btn.setToolTip('Save real-time data record!')
        save_btn.pressed.connect(self.save)

        layout.addWidget(homing_btn, 0, 0)
        layout.addWidget(reset_btn, 0, 1)
        layout.addWidget(update_btn, 0, 2)
        layout.addWidget(save_btn, 0, 3)

        return layout

    def homing(self):
        self.worker = ArmHomingThread(self.x_axis, self.y_axis)
        self.worker.start()

    def reset(self):
        self.list()
        
        self.x_axis.reset_error()
        self.y_axis.reset_error()
        
        QMessageBox.information(self, "Done!", "Record reset success!")

    def real_time_slot(self):
        self.v_btn.setEnabled(True)
        self.p_btn.setEnabled(True)
        self.f_btn.setEnabled(True)

        self.worker = ArmInfoThread(self.x_axis, self.y_axis)
        self.worker.update.connect(self.info_update_event)
        self.worker.start()

    def info_update_event(self, data):  # test
        self.current_x.append(data[0][0])
        self.position_x.append(data[0][1])
        self.velocity_x.append(data[0][2])

        self.current_y.append(data[1][0])
        self.position_y.append(data[1][1])
        self.velocity_y.append(data[1][2])

        self.f_x.setText(str(data[0][0]))
        self.p_x.setText(str(data[0][1]))
        self.v_x.setText(str(data[0][2]))

        self.f_y.setText(str(data[1][0]))
        self.p_y.setText(str(data[1][1]))
        self.v_y.setText(str(data[1][2]))

    def save(self):
        write_log('arm', 'arm_position', self.position_x[0:self.index])
        write_log('arm', 'arm_position', '\n' + str(self.position_y[0:self.index]))

        write_log('arm', 'arm_velocity', self.velocity_x[0:self.index])
        write_log('arm', 'arm_velocity', '\n' + str(self.velocity_y[0:self.index]))

        write_log('arm', 'arm_force', self.current_x[0:self.index])
        write_log('arm', 'arm_force', '\n' + str(self.current_y[0:self.index]))

        QMessageBox.information(self, "Done!", "Arm test record saved success!")


class ArmReport(QWidget):
    def __init__(self):
        super().__init__()
        self.username = 'demo'

        self.list()
        self.init()
        self.show()

    def user_changed_slot(self, username):
        self.username = username
        print("arm report: " + username)

    def list(self):
        self.force_x = []
        self.force_y = []

        self.position_x = []
        self.position_y = []

        self.velocity_x = []
        self.velocity_y = []

    def init(self):
        self.setWindowIcon(QIcon('icon/arm.PNG'))
        self.setWindowTitle('Arm Report')

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addLayout(self.info_layout())

    def info_layout(self):
        layout = QGridLayout()

        motor_1 = QLabel('Motor 1', self)
        motor_2 = QLabel('Motor 2', self)
        motor_1.setAlignment(Qt.AlignCenter)
        motor_2.setAlignment(Qt.AlignCenter)

        layout.addWidget(motor_1, 0, 1)
        layout.addWidget(motor_2, 0, 2)

        """ ********** Range ********** """

        range_lab = QLabel('max. Range (mm): ', self)

        self.range_val_1 = QLabel('12%', self)
        self.range_val_2 = QLabel('15%', self)
        self.range_val_1.setAlignment(Qt.AlignCenter)
        self.range_val_2.setAlignment(Qt.AlignCenter)

        self.range_btn = QPushButton('Chart', self)
        self.range_btn.setEnabled(False)
        self.range_btn.setToolTip('Display the range test record!')
        # self.range_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.position_1), to_clean_list(self.position_2), "Motor 1: Position record", "Motor 2: Position record", "position (mm)"))

        layout.addWidget(range_lab, 1, 0)
        layout.addWidget(self.range_val_1, 1, 1)
        layout.addWidget(self.range_val_2, 1, 2)
        layout.addWidget(self.range_btn, 1, 3)

        """ ********** Velocity ********** """

        velo_lab = QLabel('max. Velocity (mm/s): ', self)

        self.velo_val_1 = QLabel('20%', self)
        self.velo_val_2 = QLabel('23%', self)
        self.velo_val_1.setAlignment(Qt.AlignCenter)
        self.velo_val_2.setAlignment(Qt.AlignCenter)

        self.velo_btn = QPushButton('Chart', self)
        self.velo_btn.setEnabled(False)
        self.velo_btn.setToolTip('Display the velocity test record!')
        # self.velo_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.velocity_1), to_clean_list(self.velocity_2), "Motor 1: Velocity record", "Motor 2: Velocity record", "velocity (mm/s)"))

        layout.addWidget(velo_lab, 2, 0)
        layout.addWidget(self.velo_val_1, 2, 1)
        layout.addWidget(self.velo_val_2, 2, 2)
        layout.addWidget(self.velo_btn, 2, 3)

        date = QLabel('Training Date: ', self)

        self.start_date = QLabel('01.01.2023 ~', self)
        self.end_date = QLabel('01.03.2023', self)
        self.start_date.setAlignment(Qt.AlignCenter)
        self.end_date.setAlignment(Qt.AlignCenter)

        self.times = QLabel('8 times', self)
        self.times.setAlignment(Qt.AlignCenter)

        layout.addWidget(date, 3, 0)
        layout.addWidget(self.start_date, 3, 1)
        layout.addWidget(self.end_date, 3, 2)
        layout.addWidget(self.times, 3, 3)

        return layout

    def add_history(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ArmReport()
    sys.exit(app.exec_())
