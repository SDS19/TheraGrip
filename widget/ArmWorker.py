from widget.IOChart import *
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


class ArmMoveThread(QThread):
    def __init__(self, x_axis, y_axis, p1, p2, velocity, times):
        super().__init__()
        self.x_axis = x_axis
        self.y_axis = y_axis

        self.p1 = p1
        self.p2 = p2
        self.velocity = velocity
        self.times = times

    finish = pyqtSignal()

    def run(self):
        v = 80 if len(self.velocity) == 0 else int(self.velocity)
        n = 1 if len(self.times) == 0 else int(self.times)

        for i in range(int(n)):
            print("loop: " + str(i))
            self.x_axis.profile_position_mode(v, 80, self.p1[0])
            self.y_axis.profile_position_mode(v, 80, self.p1[1])
            while self.x_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
            while self.y_axis.get_actual_velocity() != 0:
                time.sleep(0.1)

            self.x_axis.profile_position_mode(80, 80, self.p2[0])
            self.y_axis.profile_position_mode(80, 80, self.p2[1])
            while self.x_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
            while self.y_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
                
        self.x_axis.profile_position_mode(v, 80, self.p1[0])
        self.y_axis.profile_position_mode(v, 80, self.p1[1])
        while self.x_axis.get_actual_velocity() != 0:
            time.sleep(0.1)
        while self.y_axis.get_actual_velocity() != 0:
            time.sleep(0.1)

        self.finish.emit()


class ArmHomingThread(QThread):
    def __init__(self, x_axis, y_axis):
        super().__init__()
        self.x_axis = x_axis
        self.y_axis = y_axis

    def run(self):
        self.x_axis.check_error()
        self.y_axis.check_error()

        if self.x_axis.error == 0 and self.y_axis.error == 0:
            self.x_axis.homing(60, 100)
            self.y_axis.homing(60, 100)
        else:
            self.x_axis.init()
            self.y_axis.init()
            self.x_axis.homing(60, 100)
            self.y_axis.homing(60, 100)


class ArmStopThread(QThread):
    def __init__(self, x_axis, y_axis):
        super().__init__()
        self.x_axis = x_axis
        self.y_axis = y_axis

    def run(self):
        self.x_axis.stop()
        self.y_axis.stop()


class ArmInfoThread(QThread):
    def __init__(self, x_axis, y_axis):
        super().__init__()
        self.x_axis = x_axis
        self.y_axis = y_axis
        
    update = pyqtSignal(object)

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.request)
        self.timer.start(100)
        self.exec_()

    def request(self):
        f_x = amp_to_force(self.x_axis.get_actual_current())
        p_x = self.x_axis.get_actual_position()
        v_x = self.x_axis.get_actual_velocity()

        f_y = amp_to_force(self.y_axis.get_actual_current())
        p_y = self.y_axis.get_actual_position()
        v_y = self.y_axis.get_actual_velocity()

        self.update.emit([[f_x, p_x, v_x], [f_y, p_y, v_y]])
