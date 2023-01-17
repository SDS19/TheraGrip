from widget.IOChart import *
from widget.HandWorker import *
from widget.UserWidget import UserHistory

test = False


class HandUser(QWidget):
    if test:
        def __init__(self):
            super().__init__()
            self.username = 'demo'

            self.init()
            self.show()
            print("test mode")
    else:
        def __init__(self, node_1, node_2):
            super().__init__()
            self.username = 'demo'

            self.node_1 = node_1
            self.node_2 = node_2

            self.list()
            self.init()
            self.show()

    def user_changed_slot(self, username):
        self.username = username
        self.user_history_widget.username = username
        print("hand user: " + username)

    def list(self):
        self.position_1 = []
        self.position_2 = []

        self.velocity_1 = []
        self.velocity_2 = []

    def init(self):
        self.setWindowIcon(QIcon('icon/close hand.PNG'))
        self.setWindowTitle('Hand User')

        layout = QVBoxLayout()
        self.setLayout(layout)

        test_group = QGroupBox('Test')
        info_group = QGroupBox('Info')
        train_group = QGroupBox('Train')

        layout.addWidget(test_group)
        layout.addWidget(info_group)
        layout.addWidget(train_group)

        test_group.setLayout(self.grip_test_layout())
        info_group.setLayout(self.info_layout())
        train_group.setLayout(self.setting_layout())

        self.timer = QTimer()
        self.timer.timeout.connect(self.record)

    """ finish ******************** Timer ******************** """

    def record(self):
        # if len(self.position_1) < 100:
        #     self.prg.setValue(len(self.position_1) + 1)
        #     self.position_1.append(1)
        self.position_record()
        self.velocity_record()

    def position_record(self):
        if len(self.position_1) < 100:
            self.prg.setValue(len(self.position_1) + 1)  # update progress bar

            p_1 = round(self.node_1.get_actual_position() * self.node_1.position_factor, 2)
            p_2 = round(self.node_2.get_actual_position() * self.node_2.position_factor, 2)

            self.position_1.append(p_1)
            self.position_2.append(p_2)

            self.range_val_1.setText(str(p_1))
            self.range_val_2.setText(str(-1 * p_2))
        else:
            self.timer.stop()
            print("QTimer stopped!")
            self.save_btn.setEnabled(True)
            self.range_btn.setEnabled(True)
            
            self.range_val_1.setText(str(abs(round(max(self.position_1) - min(self.position_1), 2))))
            self.range_val_2.setText(str(abs(round(max(self.position_2) - min(self.position_2), 2))))

    def velocity_record(self):
        if len(self.velocity_1) < 100:
            v_1 = round(self.node_1.get_actual_velocity(), 2)
            v_2 = round(self.node_2.get_actual_velocity(), 2)

            self.velocity_1.append(v_1)
            self.velocity_2.append(v_2)

            self.velo_val_1.setText(str(v_1))
            self.velo_val_2.setText(str(v_2))
        else:
            self.velo_btn.setEnabled(True)
            
            self.velo_val_1.setText(str(max(self.velocity_1)))
            self.velo_val_2.setText(str(max(self.velocity_2)))

    """ finish ******************** Grip Test ******************** """

    def grip_test_layout(self):
        layout = QGridLayout()

        label = QLabel('Grip Test: ', self)

        self.prg = QProgressBar()
        self.prg.setStyle(QStyleFactory.create("Windows"))
        self.prg.setTextVisible(True)

        self.start_btn = QPushButton('Start', self)
        self.start_btn.setToolTip('Open and close your hand as much as possible after test started!')
        self.start_btn.pressed.connect(self.start_slot)

        self.stop_btn = QPushButton('Stop', self)
        self.stop_btn.setToolTip('Stop the test!')
        self.stop_btn.setEnabled(False)
        self.stop_btn.pressed.connect(self.stop_slot)

        self.save_btn = QPushButton('Save', self)
        self.save_btn.setToolTip('Save the grip test record!')
        self.save_btn.setEnabled(False)
        self.save_btn.pressed.connect(self.save_slot)

        layout.addWidget(label, 0, 0)
        layout.addWidget(self.prg, 0, 1, 1, 2)
        layout.addWidget(self.save_btn, 0, 3)
        layout.addWidget(self.start_btn, 1, 1)
        layout.addWidget(self.stop_btn, 1, 2)

        return layout

    def start_slot(self):
        self.list()
            
        self.node_1.homing_to_actual_position()
        self.node_2.homing_to_actual_position()
        self.node_1.shut_down()
        self.node_2.shut_down()

        self.timer.start(100)  # 10 ms
        self.stop_btn.setEnabled(True)

    def stop_slot(self):
        self.timer.stop()
        self.stop_btn.setEnabled(False)

    def save_slot(self):
        self.save_btn.setEnabled(False)
        # write_config('hand', [min(self.position_1), max(self.position_1),
        #                       min(self.position_2), max(self.position_2),
        #                       max(self.velocity_1), max(self.velocity_2)])

        write_user_log(self.username, 'hand', 'position', self.position_1)
        write_user_log(self.username, 'hand', 'position', '\n' + str(self.position_2))

        write_user_log(self.username, 'hand', 'velocity', self.velocity_1)
        write_user_log(self.username, 'hand', 'velocity', '\n' + str(self.velocity_2))

        QMessageBox.information(self, 'Done!', 'Test record saved success!')

    """ finish ******************** Range Widget ******************** """

    def info_layout(self):
        layout = QGridLayout()

        motor_1 = QLabel('Motor 1', self)
        motor_2 = QLabel('Motor 2', self)
        motor_1.setAlignment(Qt.AlignCenter)
        motor_2.setAlignment(Qt.AlignCenter)

        layout.addWidget(motor_1, 0, 1)
        layout.addWidget(motor_2, 0, 2)

        """ ********** Range ********** """

        label = QLabel('max. Range (mm): ', self)

        self.range_val_1 = QLabel('0', self)
        self.range_val_2 = QLabel('0', self)
        self.range_val_1.setAlignment(Qt.AlignCenter)
        self.range_val_2.setAlignment(Qt.AlignCenter)

        self.range_btn = QPushButton('Chart', self)
        self.range_btn.setEnabled(False)
        self.range_btn.setToolTip('Display the range test record!')
        self.range_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.position_1), to_clean_list(self.position_2), "Motor 1: Position record", "Motor 2: Position record", "position (mm)"))
        # self.range_chart)

        layout.addWidget(label, 1, 0)
        layout.addWidget(self.range_val_1, 1, 1)
        layout.addWidget(self.range_val_2, 1, 2)
        layout.addWidget(self.range_btn, 1, 3)

        """ ********** Velocity ********** """

        label = QLabel('max. Velocity (mm/s): ', self)

        self.velo_val_1 = QLabel('0', self)
        self.velo_val_2 = QLabel('0', self)
        self.velo_val_1.setAlignment(Qt.AlignCenter)
        self.velo_val_2.setAlignment(Qt.AlignCenter)

        self.velo_btn = QPushButton('Chart', self)
        self.velo_btn.setEnabled(False)
        self.velo_btn.setToolTip('Display the velocity test record!')
        self.velo_btn.pressed.connect(lambda: dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), to_clean_list(self.velocity_1), to_clean_list(self.velocity_2), "Motor 1: Velocity record", "Motor 2: Velocity record", "velocity (mm/s)"))

        layout.addWidget(label, 2, 0)
        layout.addWidget(self.velo_val_1, 2, 1)
        layout.addWidget(self.velo_val_2, 2, 2)
        layout.addWidget(self.velo_btn, 2, 3)

        return layout

    """ ******************** Setting Widget ******************** """

    def setting_layout(self):
        layout = QVBoxLayout()
        layout.addLayout(self.training_layout())
        self.user_history_widget = UserHistory(self.username, 'hand')
        layout.addWidget(self.user_history_widget)
        return layout

    def training_layout(self):
        layout = QGridLayout()

        loop_lab = QLabel('loop times: ', self)
        self.loop_val = QLineEdit(str(1) if test else str(self.node_1.cycle), self)
        self.loop_val.setFixedWidth(120)
        self.loop_val.setAlignment(Qt.AlignCenter)

        self.start = QPushButton('Start', self)
        self.start.setToolTip('Start grip training!')
        self.start.pressed.connect(self.start_training_slot)

        self.stop = QPushButton('Stop', self)
        self.stop.setToolTip('Start grip training!')
        self.stop.setEnabled(False)
        self.stop.pressed.connect(self.stop_training_slot)

        layout.addWidget(loop_lab, 0, 0)
        layout.addWidget(self.loop_val, 0, 1)
        layout.addWidget(self.start, 0, 2)
        layout.addWidget(self.stop, 0, 3)

        return layout

    def config(self):        
       if not test:        
           self.node_1.start_position = min(self.position_1) / self.node_1.position_factor
           self.node_1.end_position = max(self.position_1) / self.node_1.position_factor

           self.node_2.start_position = min(self.position_2) / self.node_2.position_factor
           self.node_2.end_position = max(self.position_2) / self.node_2.position_factor

           self.node_1.set_target_velocity(max(self.velocity_1))
           self.node_2.set_target_velocity(max(self.velocity_2))
           
           self.node_1.cycle = int(self.loop_val.text())

    def start_training_slot(self):
        self.btn_enable(False)
        self.config()
        self.worker = HandMoveThread(self.node_1, self.node_2)
        self.worker.finished.connect(lambda: self.btn_enable(True))
        self.worker.start()      

    def stop_training_slot(self):
        self.btn_enable(True)
        self.worker = HandStopThread(self.node_1, self.node_2)
        self.worker.finished.connect(lambda: self.btn_enable(False))
        self.worker.start()
       
    def btn_enable(self, flag):
        self.start.setEnabled(flag)
        self.stop.setEnabled(not flag)


class HandDev(QWidget):
    if test:
        def __init__(self):
            super().__init__()
            self.username = 'demo'

            self.init()
            self.show()
            print("test mode")
    else:
        def __init__(self, node_1, node_2):
            super().__init__()
            self.username = 'demo'

            self.node_1 = node_1
            self.node_2 = node_2

            self.list()
            self.init()
            self.show()

    def user_changed_slot(self, username):
        self.username = username
        print("hand dev: " + username)

    def list(self):
        self.current_1 = []
        self.current_2 = []

        self.position_1 = []
        self.position_2 = []

        self.velocity_1 = []
        self.velocity_2 = []

    def init(self):
        self.setWindowIcon(QIcon('icon/open hand.PNG'))
        self.setWindowTitle('Hand Dev')

        layout = QGridLayout()
        self.setLayout(layout)

        self.homing_widget(layout)

        self.start_position_widget(layout)
        self.end_position_widget(layout)
        self.velocity_widget(layout)
        self.loop_widget(layout)

        self.force_info(layout)
        self.position_info(layout)
        self.velocity_info(layout)

        self.control_widget(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.record)

    """ ******************** Timer ******************** """

    def record(self):
        self.position_record()
        self.velocity_record()
        self.current_record()

    def position_record(self):
        p_1 = round(self.node_1.get_actual_position() * self.node_1.position_factor, 2)
        p_2 = -1 * round(self.node_2.get_actual_position() * self.node_2.position_factor, 2)

        self.position_1.append(p_1)
        self.position_2.append(p_2)

        self.p_val_1.setText(str(p_1))
        self.p_val_2.setText(str(p_2))

    def velocity_record(self):
        v_1 = round(self.node_1.get_actual_velocity(), 2)
        v_2 = round(self.node_2.get_actual_velocity(), 2)

        self.velocity_1.append(v_1)
        self.velocity_2.append(v_2)

        self.v_val_1.setText(str(v_1))
        self.v_val_2.setText(str(v_2))
        
    def current_record(self):
        f_1 = round(self.node_1.get_actual_current(), 2)
        f_2 = round(self.node_2.get_actual_current(), 2)

        self.current_1.append(f_1)
        self.current_2.append(f_2)

        self.f_val_1.setText(str(f_1))
        self.f_val_2.setText(str(f_2))

    """ finish ******************** homing widget ******************** """

    def homing_widget(self, layout):
        homing_lab = QLabel("Homing: ", self)

        homing_1 = QPushButton("Motor 1", self)
        homing_1.setToolTip('Homing the current position as 0 point!')
        homing_1.pressed.connect(self.homing_slot_1)

        homing_2 = QPushButton("Motor 2", self)
        homing_2.setToolTip('Homing the current position as 0 point!')
        homing_2.pressed.connect(self.homing_slot_2)

        layout.addWidget(homing_lab, 0, 0)
        layout.addWidget(homing_1, 0, 1)
        layout.addWidget(homing_2, 0, 2)

    def homing_slot_1(self):
        self.node_1.homing_to_actual_position()
        self.node_1.shut_down()

    def homing_slot_2(self):
        self.node_2.homing_to_actual_position()
        self.node_2.shut_down()

    """ finish ********** start position widget ********** """

    def start_position_widget(self, layout):
        start_label = QLabel('start position (mm): ', self)

        self.start_val_1 = QLineEdit(self)
        self.start_val_2 = QLineEdit(self)

        self.start_val_1.setAlignment(Qt.AlignCenter)
        self.start_val_2.setAlignment(Qt.AlignCenter)

        start_btn = QPushButton('Save', self)
        start_btn.setToolTip('Save the current position as start position!')
        start_btn.setFixedWidth(50)
        start_btn.pressed.connect(self.start_btn_slot)

        layout.addWidget(start_label, 1, 0)
        layout.addWidget(self.start_val_1, 1, 1)
        layout.addWidget(self.start_val_2, 1, 2)
        layout.addWidget(start_btn, 1, 3)

    def start_btn_slot(self):
        self.node_1.start_position = self.node_1.get_actual_position()
        self.node_2.start_position = self.node_2.get_actual_position()

        self.start_val_1.setText(str(round(self.node_1.start_position * self.node_1.position_factor, 2)))
        self.start_val_2.setText(str(round(self.node_2.start_position * self.node_2.position_factor, 2)))

        print("node 1 start position: " + str(self.node_1.start_position))
        print("node 2 start position: " + str(self.node_2.start_position))

    """ finish ********** end position widget ********** """

    def end_position_widget(self, layout):
        end_label = QLabel('end position  (mm): ', self)

        self.end_val_1 = QLineEdit(self)
        self.end_val_2 = QLineEdit(self)
        self.end_val_1.setAlignment(Qt.AlignCenter)
        self.end_val_2.setAlignment(Qt.AlignCenter)

        end_btn = QPushButton("Save", self)
        end_btn.setToolTip('Save the current position as end position!')
        end_btn.setFixedWidth(50)
        end_btn.pressed.connect(self.end_btn_slot)

        layout.addWidget(end_label, 2, 0)
        layout.addWidget(self.end_val_1, 2, 1)
        layout.addWidget(self.end_val_2, 2, 2)
        layout.addWidget(end_btn, 2, 3)

    def end_btn_slot(self):
        self.node_1.end_position = self.node_1.get_actual_position()
        self.node_2.end_position = self.node_2.get_actual_position()

        self.end_val_1.setText(str(round(self.node_1.end_position * self.node_1.position_factor, 2)))
        self.end_val_2.setText(str(round(-1 * self.node_2.end_position * self.node_2.position_factor, 2)))

        print("node 1 end position: " + str(self.node_1.end_position))
        print("node 2 end position: " + str(self.node_2.end_position))

    """ finish ********** velocity widget ********** """

    def velocity_widget(self, layout):
        velo_lab = QLabel('velocity (mm/s): ', self)
        if test:
            self.v_val_1 = QLineEdit(self)
            self.v_val_2 = QLineEdit(self)
        else:
            self.v_val_1 = QLineEdit(str(self.node_1.velocity), self)
            self.v_val_2 = QLineEdit(str(self.node_2.velocity), self)
        self.v_val_1.setAlignment(Qt.AlignCenter)
        self.v_val_2.setAlignment(Qt.AlignCenter)

        velo_btn = QPushButton('Save', self)
        velo_btn.setToolTip('Save the target velocity!')
        velo_btn.setFixedWidth(50)
        velo_btn.pressed.connect(self.velo_btn_slot)

        layout.addWidget(velo_lab, 3, 0)
        layout.addWidget(self.v_val_1, 3, 1)
        layout.addWidget(self.v_val_2, 3, 2)
        layout.addWidget(velo_btn, 3, 3)

    def velo_btn_slot(self):
        self.node_1.velocity = self.v_val_1.text()
        self.node_2.velocity = self.v_val_2.text()

        self.node_1.set_target_velocity(self.node_1.velocity)
        self.node_2.set_target_velocity(self.node_2.velocity)

        print("node 1 velocity: " + self.node_1.velocity)
        print("node 2 velocity: " + self.node_2.velocity)

    """ ********** loop widget ********** """

    def loop_widget(self, layout):
        loop_lab = QLabel('loop: ', self)
        if test:
            self.loop_val = QLineEdit(self)
        else:
            self.loop_val = QLineEdit(str(self.node_1.cycle), self)
        self.loop_val.setAlignment(Qt.AlignCenter)

        update_btn = QPushButton('Real-Time', self)
        update_btn.setToolTip('Start reading real-time data!')
        update_btn.pressed.connect(self.update_btn_slot)

        loop_btn = QPushButton('Save', self)
        loop_btn.setToolTip('Save the loop times!')
        loop_btn.setFixedWidth(50)
        loop_btn.pressed.connect(self.loop_btn_slot)

        layout.addWidget(loop_lab, 4, 0)
        layout.addWidget(self.loop_val, 4, 1)
        layout.addWidget(update_btn, 4, 2)
        layout.addWidget(loop_btn, 4, 3)

    def update_btn_slot(self):
        self.timer.start(100)
        self.node_1.switch_on()
        # self.worker = HandInfoThread(self.node_1, self.node_2)
        # self.worker.update.connect(self.info_update_event)
        # self.worker.start()

    def loop_btn_slot(self):
        self.node_1.cycle = int(self.loop_val.text())
        print("loop times = " + str(self.node_1.cycle))

    # def info_update_event(self, data):
    #     data_1 = data[0]
    #     data_2 = data[1]
    #
    #     self.current_1.append(data_1[0])
    #     self.current_2.append(data_2[0])
    #     self.position_1.append(data_1[1])
    #     self.position_2.append(data_2[1])
    #     self.velocity_1.append(data_1[2])
    #     self.velocity_2.append(data_2[2])
    #
    #     self.f_val_1.setText(str(data_1[0]))
    #     self.f_val_2.setText(str(data_2[0]))
    #     self.p_val_1.setText(str(data_1[1]))
    #     self.p_val_2.setText(str(data_2[1]))
    #     self.v_val_1.setText(str(data_1[2]))
    #     self.v_val_2.setText(str(data_2[2]))

    """ omit ******************** force info ******************** """

    def force_info(self, layout):
        force_lab = QLabel('real-time force (N): ', self)

        self.f_val_1 = QLabel('0', self)
        self.f_val_2 = QLabel('0', self)
        self.f_val_1.setAlignment(Qt.AlignCenter)
        self.f_val_2.setAlignment(Qt.AlignCenter)

        btn = QPushButton('Chart', self)
        btn.setToolTip('Display the real-time current chart!')
        btn.setFixedWidth(50)
        btn.pressed.connect(self.force_chart)

        layout.addWidget(force_lab, 5, 0)
        layout.addWidget(self.f_val_1, 5, 1)
        layout.addWidget(self.f_val_2, 5, 2)
        layout.addWidget(btn, 5, 3)

    def force_chart(self):
        dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), self.current_1, self.current_2, "Motor 1: Current record", "Motor 2: Current record", "current (ma)")

    """ ******************** position info ******************** """

    def position_info(self, layout):
        p_lab = QLabel('real-time position (mm): ', self)

        self.p_val_1 = QLabel('0', self)
        self.p_val_2 = QLabel('0', self)
        self.p_val_1.setAlignment(Qt.AlignCenter)
        self.p_val_2.setAlignment(Qt.AlignCenter)

        btn = QPushButton('Chart', self)
        btn.setToolTip('Display the real-time position chart!')
        btn.setFixedWidth(50)
        btn.pressed.connect(self.position_chart)

        layout.addWidget(p_lab, 6, 0)
        layout.addWidget(self.p_val_1, 6, 1)
        layout.addWidget(self.p_val_2, 6, 2)
        layout.addWidget(btn, 6, 3)
        
    def position_chart(self):
        dual_plot(time.strftime('%d-%m-%Y %H:%M:%S'), self.position_1, self.position_2, "Motor 1: Position record", "Motor 2: Position record", "position (mm)")

    """ ******************** velocity info ******************** """

    def velocity_info(self, layout):
        velo_lab = QLabel('real-time velocity (mm/s): ', self)

        self.v_val_1 = QLabel('0', self)
        self.v_val_2 = QLabel('0', self)
        self.v_val_1.setAlignment(Qt.AlignCenter)
        self.v_val_2.setAlignment(Qt.AlignCenter)

        btn = QPushButton('Chart', self)
        btn.setToolTip('Display the real-time velocity chart!')
        btn.setFixedWidth(50)
        btn.pressed.connect(self.velocity_chart)

        layout.addWidget(velo_lab, 7, 0)
        layout.addWidget(self.v_val_1, 7, 1)
        layout.addWidget(self.v_val_2, 7, 2)
        layout.addWidget(btn, 7, 3)
        
    def velocity_chart(self):
        triple_plot(time.strftime('%d-%m-%Y %H:%M:%S'), self.velocity_1, self.velocity_2, 'Motor 1: Velocity record', 'Motor 2: Velocity record', 'resultant velocity', 'velocity (mm/s)')

    """ ******************** control widget ******************** """

    def control_widget(self, layout):
        start_btn = QPushButton('Start', self)
        stop_btn = QPushButton('Stop', self)
        save_btn = QPushButton('Save', self)
        save_btn.setToolTip('Save the test record!')
        save_btn.setFixedWidth(50)

        start_btn.pressed.connect(self.start_slot)
        stop_btn.pressed.connect(self.stop_slot)
        save_btn.pressed.connect(self.save_slot)

        layout.addWidget(start_btn, 9, 1)
        layout.addWidget(stop_btn, 9, 2)
        layout.addWidget(save_btn, 9, 3)

    def start_slot(self):
        self.worker = HandMoveThread(self.node_1, self.node_2)
        self.worker.start()
        # self.worker.finished.connect(self.move_finished_event)

    def move_finished_event(self):  # need to be fixed
        print(len(self.current_1))
        print(len(self.current_2))

        print(len(self.position_1))
        print(len(self.position_2))

        print(len(self.velocity_1))
        print(len(self.velocity_2))

    def stop_slot(self):
        self.worker = HandStopThread(self.node_1, self.node_2)
        self.worker.start()

    def save_slot(self):
        write_user_log(self.username, 'hand', 'current', self.current_1)
        write_user_log(self.username, 'hand', 'current', '\n' + str(self.current_2))

        write_user_log(self.username, 'hand', 'position', self.position_1)
        write_user_log(self.username, 'hand', 'position', '\n' + str(self.position_2))

        write_user_log(self.username, 'hand', 'velocity', self.velocity_1)
        write_user_log(self.username, 'hand', 'velocity', '\n' + str(self.velocity_2))

        QMessageBox.information(self, "Done!", "Hand test record saved success!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HandUser()
    sys.exit(app.exec_())
