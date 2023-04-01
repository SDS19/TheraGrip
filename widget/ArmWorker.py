from widget.IOChart import *
from widget.VelocityCurve import *
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

n = 5  # number of interpolation point


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
        
        self.stop = False
        self.shut_down = False

    finish = pyqtSignal()

    def run(self):        
        v = 80 if len(self.velocity) == 0 else int(self.velocity)
        times = 1 if len(self.times) == 0 else int(self.times)

        for i in range(int(times)):            
            self.x_axis.profile_position_mode(v, 80, self.p1[0])
            self.y_axis.profile_position_mode(v, 80, self.p1[1])
            while self.x_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
            while self.y_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
                
            if self.stop or self.shut_down:
                break
                
            # define the waiting time before movement
#             time.sleep(3)
#             print("forward wait: 3 s")

            self.x_axis.profile_position_mode(80, 80, self.p2[0])
            self.y_axis.profile_position_mode(80, 80, self.p2[1])
            while self.x_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
            while self.y_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
                
            if self.stop or self.shut_down:
                break
                
#             time.sleep(3)
#             print("backward wait: 3 s")

        if self.shut_down:
            return
                
        self.x_axis.profile_position_mode(v, 80, self.p1[0])
        self.y_axis.profile_position_mode(v, 80, self.p1[1])
        while self.x_axis.get_actual_velocity() != 0:
            time.sleep(0.1)
        while self.y_axis.get_actual_velocity() != 0:
            time.sleep(0.1)
            
        
        # self.move_1()
#         self.x_axis.profile_velocity_mode(100, 100)
        
#         velo_x_mat = convertVeloListToByte(velo_x_list, forward_x)
#         velo_y_mat = convertVeloListToByte(velo_y_list, forward_y)
#         
#         acc_x_mat = 
#         acc_y_mat = convertAccListToByte(acc_y_list)
#         
#         velo_acc_x_mat = conVeloAccMat(velo_x_mat, acc_x_mat)
#         velo_acc_y_mat = conVeloAccMat(velo_y_mat, acc_y_mat)
#         
#         self.x_axis.ProfVeloMode(velo_acc_x_mat)

        self.finish.emit()

    """ ********** optimized start ********** """

    def move_1(self):        
        p_list = get_position_list(n, self.p1, self.p2)
        print("position: " + str(p_list))

        xyv_list = get_xy_velocity_list(n, self.p1, self.p2)
        v_x_list = xyv_list[0]
        v_y_list = xyv_list[1]
        v_list = xyv_list[2]
        print("velocity: " + str(v_list))
        
        t_list = get_time_list(v_list, self.p1, self.p2)

        a_x_list = get_acceleration_list(v_x_list, t_list)
        a_y_list = get_acceleration_list(v_y_list, t_list)
        print("acc: " + str(a_x_list))

        for i in range(1, n + 1):
            print("i: " + str(i))
            
            p = p_list[i]
            p_x = p[0]
            p_y = p[1]
            print("p: " + str(p))

            v_x = v_x_list[i]
            v_y = v_y_list[i]
            print("v_x: " + str(v_x))
            print("v_y: " + str(v_y))

            a_x = a_x_list[i - 1]
            a_y = a_y_list[i - 1]
            print("a_x: " + str(a_x))
            print("a_y: " + str(a_y))
            
            self.x_axis.profile_position_mode(v_x, a_x, p_x)
            self.y_axis.profile_position_mode(v_y, a_y, p_y)

#             self.x_axis.profile_velocity_mode(v_x, a_x)
#             self.y_axis.profile_velocity_mode(v_y, a_y)

            while self.x_axis.get_actual_position() * self.factor <= p_x and self.y_axis.get_actual_position() * self.factor <= p_y:
                time.sleep(0.01)

    def move_2(self):
        p_list = get_position_list(n, self.p1, self.p2)

        xyv_list = get_xy_velocity_list(n, self.p1, self.p2)
        v_x_list = xyv_list[0]
        v_y_list = xyv_list[1]
        v_list = xyv_list[2]

        t_list = get_time_list(v_list, self.p1, self.p2)

        a_x_list = get_acceleration_list(v_x_list, t_list)
        a_y_list = get_acceleration_list(v_y_list, t_list)

        for i in range(1, n):
            p = p_list[i]
            p_x = p[0]
            p_y = p[1]

            v_x = v_x_list[i]
            v_y = v_y_list[i]

            a_x = a_x_list[i - 1]
            a_y = a_y_list[i - 1]

            self.x_axis.profile_velocity_mode(v_x, a_x)
            self.y_axis.profile_velocity_mode(v_y, a_y)

            while self.x_axis.get_actual_position() * self.factor <= p_x and self.y_axis.get_actual_position() * self.factor <= p_y:
                time.sleep(0.01)

        # profile position mode in last segment
        p_x = self.p2[0]
        p_y = self.p2[1]

        v_x = v_x_list[-2]
        v_y = v_y_list[-2]

        a_x = a_x_list[-1]
        a_y = a_y_list[-1]

        self.x_axis.profile_position_mode(v_x, a_x, p_x)
        self.y_axis.profile_position_mode(v_y, a_y, p_y)

    """ ********** optimized end ********** """

def to_byte(x):
    return list(int(x * factor).to_bytes(4, byteorder='little', signed=True))

def negNumToFourByte(num):  # check negative num 23.02
    byte_list = [255, 255, 255, 255]
    num = abs(num)
    byte_list = to_byte(num)
    for i in range(0, 4):
        byte_list[i] = 255 - byte_list[i]
    return byte_list
    
def convertVeloListToByte(velo_list, forward):
    row = len(velo_list)
    velo_mat = np.arange(row*4).reshape(row, 4)              
        
    if forward:
        for i in range(0, row):
            velo_mat[i] = negNumToFourByte(velo_list[i])
    else:
        for i in range(0, row):
            velo_mat[i] = to_byte(velo_list[i])  
    
    velo_mat[0] = [0,0,0,0]
    velo_mat[row-1] = [0,0,0,0]

    return velo_mat    
    
def convertAccListToByte(acc_list):
    row = len(acc_list)
    acc_mat = np.arange(row*4).reshape(row, 4)
    for i in range(0, row):
        acc_mat[i] = to_byte(abs(acc_list[i]))
    return acc_mat
    
def conVeloAccMat(velo_mat, acc_mat):
    return np.hstack((velo_mat, acc_mat))


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


class ArmStopThread(QThread):  # finish
    def __init__(self, x_axis, y_axis):
        super().__init__()
        self.x_axis = x_axis
        self.y_axis = y_axis

    def run(self):  # stop the current movement
        stop = True
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