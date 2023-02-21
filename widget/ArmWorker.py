import math

import numpy as np

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

        self.factor = x_axis.SI_unit_factor

    finish = pyqtSignal()

    def run(self):        
        v = 80 if len(self.velocity) == 0 else int(self.velocity)
        n = 1 if len(self.times) == 0 else int(self.times)

        for i in range(int(n)):
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

    def to_byte(self, x):
        return list(int(x * self.factor).to_bytes(4, byteorder='little', signed=True))

    def convertVeloListToByte(self, velo_list, forward):
        row = len(velo_list)
        velo_mat = np.arange(row * 4).reshape(row, 4)
        if forward == False:
            for i in range(0, row):
                velo_mat[i] = self.to_byte(velo_list[i])
        if forward == True:
            for i in range(0, row):
                velo_mat[i] = self.to_byte(velo_list[i])
        velo_mat[0] = [0, 0, 0, 0]
        velo_mat[row - 1] = [0, 0, 0, 0]
        return velo_mat

    def get_velocity_byte_list(self, v_list):
        v_byte_list = []
        for v in v_list:
            v_byte_list.append(self.to_byte(v))
        return v_byte_list


""" ******************** Nils Hoppe human mode 14.02.2023 ~ 17.02.2023 ******************** """


# Nils Hoppe paper P118
def mod_velocity_curve(x):
    y = -5.83397691012945e-14 * pow(x, 9) + 4.01458396693356e-11 * pow(x, 8) - 9.62482037096911e-9 * pow(x, 7) + \
           1.06977262917339e-6 * pow(x, 6) - 5.68239363212274e-5 * pow(x, 5) + 0.00125022968775769 * pow(x, 4) - \
           0.0124822800434351 * pow(x, 3) + 0.531322885004075 * pow(x, 2) - 0.240497493514033 * x + 0.234808880863676
    return y / 2


# n: sample number
def show_mod_velocity_curve(n):
    single_plot(get_velocity_list(n), "velocity", "modified velocity curve")


""" ********** volecity list ********** """


# get velocity list based on sample number
def get_velocity_list(n):
    v_list = []
    v_interval = 100 / n
    for i in range(n + 1):  # n+1 => symmetrical
        v_list.append(round(mod_velocity_curve(i * v_interval)))
    v_list[-1] = 0  # border condition
    return v_list


# get velocity list in x and y axis (x^2 + y^2 = v^2)
# d_x: distance in x axis; d_y: distance in y axis
def get_xy_velocity_list(n, d_x, d_y):
    x_list = []
    y_list = []
    v_list = []
    v_interval = 100 / n
    for i in range(n + 1):
        v_list.append(mod_velocity_curve(i * v_interval))
    v_list[0] = v_list[-1] = 0  # border condition

    deg = math.degrees(math.atan(d_y / d_x))
    for v in v_list:
        x_list.append(v * math.cos(math.radians(deg)))
        y_list.append(v * math.sin(math.radians(deg)))

    return [x_list, y_list, v_list]


""" ********** time list ********** """


# time = distance / mean(velocity)
def get_time_list(d, v_list):
    d_interval = d / (len(v_list) - 1)
    t_list = [0] * len(v_list)
    for i in range(1, len(v_list)):
        v_mean = v_list[i - 1] + (v_list[i] - v_list[i - 1]) / 2
        t_list[i] = d_interval / v_mean
    return t_list


""" ********** acceleration list ********** """


# abs(acceleration) = abs(velocity) / time
def get_acc_list(v_list, t_list):
    a_list = [0]
    for i in range(1, len(v_list)):
        a_list.append(round(abs(v_list[i] - v_list[i - 1]) / t_list[i]))  # abs
    return a_list


def to_byte(x):
    return list(int(x).to_bytes(4, byteorder='little', signed=True))

def convertVeloListToByte(velo_list, forward):
    row = len(velo_list)
    velo_mat = np.arange(row * 4).reshape(row, 4)
    if forward == False:
        for i in range(0, row):
            velo_mat[i] = to_byte(velo_list[i])
    if forward == True:
        for i in range(0, row):
            velo_mat[i] = to_byte(velo_list[i])
    velo_mat[0] = [0, 0, 0, 0]
    velo_mat[row - 1] = [0, 0, 0, 0]
    return velo_mat

def get_velocity_byte_list(v_list):
    v_byte_list = []
    for v in v_list:
        v_byte_list.append(to_byte(v))
    return v_byte_list



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


def checkDirection(s, t):
    if s >= t:
        forward = True
    else:
        forward = False
    return forward


if __name__ == '__main__':
    # show_mod_velocity_curve(3)
    start_x = 250
    start_y = 250

    target_x = 150
    target_y = 100

    d_x = abs(start_x - target_x)
    d_y = abs(start_y - target_y)

    forward_x = checkDirection(start_x, target_x)
    forward_y = checkDirection(start_y, target_y)

    print(forward_x)  # ???
    print(forward_y)  # ???

    y = get_velocity_list(10)



