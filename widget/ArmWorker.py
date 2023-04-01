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
        
#         start_x = self.p1[0]
#         start_y = self.p1[1]
#         
#         end_x = self.p2[0]
#         end_y = self.p2[1]
#         
#         v_a_matrix = self.get_list(n, [start_x, start_y], [end_x, end_y])
#         
#         for i in range(times):
#             print("start point: " + str(start_x) + ', '+ str(start_y))
#             self.x_axis.profile_position_mode(80, 80, start_x)
#             self.y_axis.profile_position_mode(80, 80, start_x)
#                         
#             while self.x_axis.get_actual_velocity() != 0 or self.y_axis.get_actual_velocity() != 0:
#                 time.sleep(0.1)
#                     
#             print("target point: " + str(end_x) + ', '+ str(end_y))
#             self.move(self.p1, self.p2, v_a_matrix[0], v_a_matrix[1])

        for i in range(int(times)):            
            self.x_axis.profile_position_mode(v, 80, self.p1[0])
            self.y_axis.profile_position_mode(v, 80, self.p1[1])
            while self.x_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
            while self.y_axis.get_actual_velocity() != 0:
                time.sleep(0.1)
                
            if self.stop or self.shut_down:
                break
                
            # define the waiting time between movement
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


        self.finish.emit()
        
    """ ******************** to_byte ******************** """

    def to_byte(self, x):  # finish
        return list(int(x * self.factor).to_bytes(4, byteorder='little', signed=True))


    def neg_to_byte(self, num):  # check negative num 23.02
        byte_list = self.to_byte(abs(num))
        for i in range(4):
            byte_list[i] = 255 - byte_list[i]
        return byte_list

    def v_to_byte(self, v_list, forward):  # finish
        row = len(v_list)
        v_mat = np.arange(row * 4).reshape(row, 4)
    
        for i in range(0, row):
            if forward:
                v_mat[i] = self.neg_to_byte(v_list[i])
            else:
                v_mat[i] = self.to_byte(v_list[i])
    
        v_mat[0] = [0, 0, 0, 0]
        v_mat[row-1] = [0,0,0,0]

        return v_mat


    def a_to_byte(self, a_list):  # finish
        row = len(a_list)
        a_mat = np.arange(row * 4).reshape(row, 4)
        for i in range(0, row):
            a_mat[i] = self.to_byte(abs(a_list[i]))
        return a_mat
    
    def get_list(self, n, start_point, end_point):
        start_x = start_point[0]
        start_y = start_point[1]

        end_x = end_point[0]
        end_y = end_point[1]
    
        d_x = abs(end_x - start_x)
        d_y = abs(end_y - start_y)
    
        forward_x = direction(start_x, end_x)
        forward_y = direction(start_y, end_y)
    
        v_x_list = []
        v_y_list = []
    
        if d_x != 0 and d_y != 0:
            (v_x_list, v_y_list, v_list) = get_xy_velocity_list(n, d_x, d_y)

            t_x_list = get_time_list(d_x, n, v_x_list)
            t_y_list = get_time_list(d_y, n, v_y_list)

            a_x_list = get_acceleration_list(t_x_list, v_x_list)
            a_y_list = get_acceleration_list(t_y_list, v_y_list)
    
#         time_n_list = calcNewCycleList(t_x_list, t_y_list)

            v_x_byte = self.v_to_byte(v_x_list, forward_x)
            v_y_byte = self.v_to_byte(v_y_list, forward_y)
        
            a_x_byte = self.a_to_byte(a_x_list)
            a_y_byte = self.a_to_byte(a_y_list)
        
            v_a_x_byte = conVeloAccMat(v_x_byte, a_x_byte)
            v_a_y_byte = conVeloAccMat(v_y_byte, a_y_byte)

#         op_time_n_list = opCycleList(time_n_list)

        if d_y == 0.0:
            v_x_list = get_velocity_list(n)
            v_y_list = [0] * len(v_x_list)
            v_list = v_x_list
        
            t_x_list = get_time_list(d_x, n, v_x_list)
            a_x_list = get_acceleration_list(t_x_list, v_x_list)
        
            v_x_byte = self.v_to_byte(v_x_list, forward_x)
            a_x_byte = self.a_to_byte(a_x_list)

            v_a_x_byte = conVeloAccMat(v_x_byte, a_x_byte)
            v_a_y_byte = []

#         time_n_list = t_x_list
# 
#         op_time_n_list = opCycleList(time_n_list)

        if d_x == 0.0:
            v_y_list = get_velocity_list(n)
            v_x_list = [0] * len(v_y_list)
            v_list = v_y_list

            t_y_list = get_time_list(d_y, n, v_y_list)
            a_y_list = get_acceleration_list(t_y_list, v_y_list)
        
            v_y_byte = self.v_to_byte(v_y_list, forward_y)
            a_y_byte = self.a_to_byte(a_y_list)

            v_a_y_byte = conVeloAccMat(v_y_byte, a_y_byte)
            v_a_x_byte = []

#         time_n_list = t_y_list
#         op_time_n_list = opCycleList(time_n_list)

        return [v_a_x_byte, v_a_y_byte]
    
    
    """ ********** optimized start ********** """
    
    def move(self, start_point, end_point, v_a_x_mat, v_a_y_mat):
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]

        d_x = end_x - start_x
        d_y = end_y - start_y
        print("d_x: " + str(d_x))
        print("d_y: " + str(d_y))
    
        p_list = get_position_list(n, start_point, end_point)
    
        if d_x != 0.0 and d_y != 0.0:
            for i in range(1, n + 1):            
                self.x_axis.profile_velocity_mode(v_a_x_mat[i])
                self.y_axis.profile_velocity_mode(v_a_y_mat[i])
            
                p_x = p_list[i][0]
                p_y = p_list[i][1]
            
                if d_x >= 0 and d_y >= 0:
                    print("+, +")
                    while self.x_axis.get_actual_position() < p_x and self.y_axis.get_actual_position() < p_y: 
                        self.position_condition(10, end_x, end_y)
                elif d_x < 0 and d_y >= 0:
                    print("-, +")
                    while self.x_axis.get_actual_position() > p_x and self.y_axis.get_actual_position() < p_y:
                        self.position_condition(10, end_x, end_y)
                elif d_x >= 0 and d_y < 0:
                    print("+, -")
                    while self.x_axis.get_actual_position() < p_x and self.y_axis.get_actual_position() > p_y:
                        self.position_condition(10, end_x, end_y)
                elif d_x < 0 and d_y < 0:
                    print("-,-")
                    while self.x_axis.get_actual_position() > p_x and self.y_axis.get_actual_position() > p_y:
                        self.position_condition(10, end_x, end_y)
        
            print("Stop Position: " + str(self.x_axis.get_actual_position()) + ", " + str(self.y_axis.get_actual_position()))

        if d_x != 0.0 and d_y == 0.0:
            for i in range(1, n + 1):
                self.x_axis.profile_velocity_mode(v_a_x_mat[i])
            
                p_x = p_list[i][0]
            
                if d_x >= 0:
                    print("+x")
                    while self.x_axis.get_actual_position() < p_x:
                        if abs(self.x_axis.get_actual_position() - end_x) <= 20:
                            self.x_axis.profile_position_mode(100, 100, end_x)
                elif d_x < 0:
                    print("-x")
                    while self.x_axis.get_actual_position() > p_x:
                        if abs(self.x_axis.get_actual_position() - end_x) <= 20:
                            self.x_axis.profile_position_mode(100, 100, end_x)
                
            print("Stop Position: " + str(self.x_axis.get_actual_position()) + ", " + str(self.y_axis.get_actual_position()))

        if d_x == 0.0 and d_y != 0.0:
            for i in range(1, n + 1):
                self.y_axis.profile_velocity_mode(v_a_y_mat[i])
            
                p_y = p_list[i][1]
            
                if d_y >= 0:
                    print("+y")
                    while self.y_axis.get_actual_position() < p_y:
                        if abs(self.y_axis.get_actual_position() - end_y) <= 10:
                            self.y_axis.profile_position_mode(100, 100, end_y)
                elif d_y < 0:
                    print("-y")
                    while self.y_axis.get_actual_position() > p_y:
                        print(p_y)
                        if abs(self.y_axis.get_actual_position() - end_y) <= 10:
                            self.y_axis.profile_position_mode(100, 100, end_y)
                        
            print("Stop Position: " + str(self.x_axis.get_actual_position()) + ", " + str(self.y_axis.get_actual_position()))

    def position_condition(self, distance, end_x, end_y):
        if abs(self.x_axis.get_actual_position() - end_x) <= distance and abs(self.y_axis.get_actual_position() - end_y) <= distance:
            print("End Position: " + str(end_x) + ", " + str(end_y))
            self.x_axis.profile_position_mode(100, 100, end_x)
            self.y_axis.profile_position_mode(100, 100, end_y)
        time.sleep(0.01)

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

            self.x_axis.profile_velocity_mode(v_x, a_x)
            self.y_axis.profile_velocity_mode(v_y, a_y)

            while self.x_axis.get_actual_position() <= p_x and self.y_axis.get_actual_position() <= p_y:
                time.sleep(0.01)


    """ ********** optimized end ********** """


def conVeloAccMat(v_byte, a_byte):
        return np.hstack((v_byte, a_byte))


def direction(start, end):
    return True if start >= end else False


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