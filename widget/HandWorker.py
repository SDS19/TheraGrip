import time
from PyQt5.Qt import *


class HandInfoThread(QThread):
    def __init__(self, node_1, node_2):
        super().__init__()
        self.node_1 = node_1
        self.node_2 = node_2

    update = pyqtSignal(object)

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.request)
        self.timer.start(100)
        self.exec_()

    def request(self):
        print(0)
        #data_1 = self.node_1.rpdo()
        #data_2 = self.node_2.rpdo()

        #f_1 = round(data_1[0], 2)
        #f_2 = round(data_2[0], 2)

        #p_1 = round(data_1[1] * self.node_1.position_factor, 2)
        #p_2 = -1 * round(data_1[1] * self.node_2.position_factor, 2)

        #v_1 = round(data_1[2], 2)
        #v_2 = round(data_1[2], 2)

        #self.update.emit([[f_1, p_1, v_1], [f_2, p_2, v_2]])


class HandMoveThread(QThread):
    finished = pyqtSignal()
    
    def __init__(self, node_1, node_2):
        super().__init__()
        self.node_1 = node_1
        self.node_2 = node_2

    def run(self):
        self.movement()
        self.finished.emit()
        self.node_1.shut_down()
        self.node_2.shut_down()
        self.exec_()

    def movement(self):
        self.node_1.set_profile_position_mode()
        self.node_2.set_profile_position_mode()
        self.node_2.set_negative_move_direction()

        for i in range(0, int(self.node_1.cycle)):
            self.node_1.move_to_target_position(self.node_1.start_position)
            self.node_2.move_to_target_position(self.node_2.start_position)
            while self.node_2.get_actual_velocity() != 0:
                time.sleep(0.01)
            while self.node_1.get_actual_velocity() != 0:
                time.sleep(0.01)

            self.node_1.move_to_target_position(self.node_1.end_position)
            self.node_2.move_to_target_position(self.node_2.end_position)
            while self.node_2.get_actual_velocity() != 0:
                time.sleep(0.01)
            while self.node_1.get_actual_velocity() != 0:
                time.sleep(0.01)


class HandStopThread(QThread):
    finished = pyqtSignal()

    def __init__(self, node_1, node_2):
        super().__init__()
        self.node_1 = node_1
        self.node_2 = node_2

    def run(self):
        self.node_1.shut_down()
        self.node_2.shut_down()
        self.finished.emit()
