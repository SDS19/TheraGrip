import os
import sys
import math
import time
import socket

debug = False


class D1:
    def __init__(self, ip, port, axis):
        self.ip = ip
        self.Socket = port
        self.axis = axis

        self.error = 0

        # 6041h: Statusword
        self.status_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2])

        # 6040h: Controlword
        self.shutdown_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 6, 0])
        self.switchOn_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 7, 0])
        self.enableOperation_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 0])

        # Controlword 6040h to reset Motor ( bit8 = 1)
        self.reset_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 0, 1])
        self.resetError_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 143, 0])

        # Read Object 60FDh for Status of digital Inputs
        self.DInputs_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 253, 0, 0, 0, 0, 4])

        # Read Obejct 6092h subindex 1 for the feed rate
        self.feedrate_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 146, 1, 0, 0, 0, 4])

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('failed to create socket')

        self.s.connect((ip, port))
        print(self.axis + ' Socket created')

        self.init()

        self.get_SI_unit_factor()

    def init(self):
        self.command(self.resetError_array)
        self.command(self.shutdown_array)
        self.command(self.switchOn_array)
        self.command(self.enableOperation_array)

    def shut_down(self):
        self.command(self.resetError_array)
        self.command(self.shutdown_array)

    def command(self, data):
        self.s.send(data)
        return list(self.s.recv(24))

    def status(self):
        return self.command(self.status_array)

    def readDigitalInput(self):
        return self.command(self.DInputs_array)

    def check_error(self):
        if (self.status() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 22]
                or self.status() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 6]
                or self.status() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 34]
                or self.status() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 2]):
            self.error = 1
        else:
            self.error = 0
            
    def reset_error(self):
        return self.command(self.resetError_array)

    """ **************************************** read value **************************************** """

    def get_actual_velocity(self):
        ans_velocity = self.command(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 108, 0, 0, 0, 0, 4]))
        act_velocity = abs(int.from_bytes(ans_velocity[19:], byteorder='little', signed=True) / self.SI_unit_factor)
        return act_velocity

    def get_actual_position(self):
        ans_position = self.command(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 100, 0, 0, 0, 0, 4]))
        act_position = int.from_bytes(ans_position[19:], byteorder='little') / self.SI_unit_factor
        self.position = act_position
        return act_position

    def get_actual_current(self):  # 6078h: Current Actual Value
        current = self.command(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 120, 0, 0, 0, 0, 4]))
        return int.from_bytes(current[19:], byteorder='little')

    """ **************************************** mode **************************************** """

    def mode(self, mode):
        # 6060h: Modes of Operation (P174 N.17)
        self.command(bytearray([0, 0, 0, 0, 0, 14, 0, 43, 13, 1, 0, 0, 96, 96, 0, 0, 0, 0, 1, mode]))
        # 6061h: Modes Display (P174 N.19)
        while (self.command(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 97, 0, 0, 0, 0, 1])) !=
               [0, 0, 0, 0, 0, 14, 0, 43, 13, 0, 0, 0, 96, 97, 0, 0, 0, 0, 1, mode]):
            time.sleep(0.1)

    def start(self):  # 6040h: Controlword => Start Movement (bit 4 = 1)
        self.command(bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 31, 0]))

    def stop(self):
        self.command(bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 1]))

    def homing(self, velo, acc):
        self.mode(6)
        self.command(self.enableOperation_array)

        self.command(bytearray([0, 0, 0, 0, 0, 17, 0, 43, 13, 1, 0, 0, 96, 146, 1, 0, 0, 0, 4, 24, 21, 0, 0]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 0, 43, 13, 1, 0, 0, 96, 146, 2, 0, 0, 0, 4, 1, 0, 0, 0]))

        v_byte = self.to_byte(velo)  # 6099h_01h Endlagenschaltersuchgeschwindigkeit
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 153, 1, 0, 0, 0, 4, v_byte[0], v_byte[1], v_byte[2], v_byte[3]]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 153, 2, 0, 0, 0, 4, v_byte[0], v_byte[1], v_byte[2], v_byte[3]]))

        a_byte = self.to_byte(acc)  # 609Ah Homing acceleration
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 154, 0, 0, 0, 0, 4, a_byte[0], a_byte[1], a_byte[2], a_byte[3]]))

        self.start()  # Enable Operation to set bit 4 of the controlword to low again

        print('\nWait Homing', end='')
        while (self.status() != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]
               and self.status() != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 6]
               and self.status() != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 34]
               and self.status() != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 2]):
            time.sleep(0.01)
            print(".", end='')
        print('\n' + self.axis + " homing success!")

    def get_SI_unit_factor(self):
        self.SI_unit_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 168, 0, 0, 0, 0, 4])
        byte_2 = int.from_bytes(self.command(self.SI_unit_array)[21:22], byteorder='big')
        byte_3 = int.from_bytes(self.command(self.SI_unit_array)[22:], byteorder='little')
        if byte_2 == 1:
            if byte_3 > 5:
                self.SI_unit_factor = (10 ** -3) / (10 ** (byte_3 - 256))
            if byte_3 < 5:
                self.SI_unit_factor = (10 ** -3) / (10 ** byte_3)
        elif byte_2 == 65:
            if byte_3 > 5:
                self.SI_unit_factor = (10 ** (-1 * (byte_3 - 256)))
            if byte_3 < 5:
                self.SI_unit_factor = (10 ** (-1 * byte_3))
        # return self.SI_unit_factor

    def to_byte(self, x):
        return list(int(x * self.SI_unit_factor).to_bytes(4, byteorder='little', signed=True))

    def profile_position_mode(self, velo, acc, pos):
        self.mode(1)  # Set Profile Position Mode (Byte 19 = 1)
        self.command(self.enableOperation_array)

        v_byte = self.to_byte(velo)  # 6081h Profile Velocity
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 129, 0, 0, 0, 0, 4, v_byte[0], v_byte[1], v_byte[2], v_byte[3]]))

        a_byte = self.to_byte(acc)  # 6083h Profile Acceleration; 6084h Profile Deceleration
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, a_byte[0], a_byte[1], a_byte[2], a_byte[3]]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 132, 0, 0, 0, 0, 4, a_byte[0], a_byte[1], a_byte[2], a_byte[3]]))

        p_byte = self.to_byte(pos)  # 607Ah Target Position
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 122, 0, 0, 0, 0, 4, p_byte[0], p_byte[1], p_byte[2], p_byte[3]]))

        self.start()

        time.sleep(0.1)
        while (self.status() != [0, 0, 0, 0, 0, 15, 1, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]
               and self.status() != [0, 0, 0, 0, 0, 15, 1, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 22]):
            break

    """ ******************** Nils Hoppe human mode 14.02.2023 ~ 17.02.2023 ******************** """

    def ProfVeloMode(self, v_list):
        self.mode(3)
        self.command(self.enableOperation_array)
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, v_list[4], v_list[5], v_list[6], v_list[7]]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 132, 0, 0, 0, 0, 4, v_list[4], v_list[5], v_list[6], v_list[7]]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 255, 0, 0, 0, 0, 4, v_list[0], v_list[1], v_list[2], v_list[3]]))

    # need to be optimized
    def profile_velocity_mode(self, velo, acc):
        v_byte = self.to_byte(velo)
        print(v_byte)
        a_byte = self.to_byte(acc)
        print(a_byte)

        self.mode(3)
        self.command(self.enableOperation_array)
        
        # 6083h Profile Acceleration; 6084h Profile Deceleration
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, a_byte[0], a_byte[1], a_byte[2], a_byte[3]]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 132, 0, 0, 0, 0, 4, a_byte[0], a_byte[1], a_byte[2], a_byte[3]]))
        self.command(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 255, 0, 0, 0, 0, 4, v_byte[0], v_byte[1], v_byte[2], v_byte[3]]))

        
        


