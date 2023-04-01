import socket
import time
import math as m
import struct
import PySimpleGUI as sg
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
import openpyxl as xl
import Handeinheit as hand
import os
import canopen
from canopen.profiles.p402 import BaseNode402


debug = False


class Motor:
    def __init__(self, IP_Adress, Port, Axis):
        
        self.IPAdress = IP_Adress
        self.Socket = Port
        self.Axis = Axis
        self.error = 0
        self.positon = 250.0
        
        # Statusword 6041h
        # Status request
        #status = [0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2]
        self.status_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2])
        #print(status_array)

        # Controlword 6040h
        # Command: Shutdown
        #shutdown = [0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 6, 0]
        self.shutdown_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 6, 0])
        #print(shutdown_array)

        # Controlword 6040h
        # Command: Switch on
        #switchOn = [0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 7, 0]
        self.switchOn_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 7, 0])
        #print(switchOn_array)

        # Controlword 6040h
        # Command: enable Operation
        #enableOperation = [0, 0, 0, 0, 0, 15, 0, 43,13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 0]
        self.enableOperation_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43,13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 0])
        #print(enableOperation_array)

        # Controlword 6040h
        # Command: stop motion
        #stop = [0, 0, 0, 0, 0, 15, 0, 43,13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 1]
        self.stop_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43,13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 1])
        #print(stop_array)

        # Controlword 6040h
        # Command: reset dryve
        #reset = [0, 0, 0, 0, 0, 15, 0, 43,13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 0, 1]
        self.reset_array = bytearray([0, 0, 0, 0, 0, 15, 0, 43,13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 0, 1])
        #print(reset_array)
        
        self.SI_unit_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 168, 0, 0, 0, 0, 4])
        
        self.DInputs_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 253, 0, 0, 0, 0, 4])
        
        self.feedrate_array = bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 146, 1, 0, 0, 0, 4])
        

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('failed to create sockt')

        self.s.connect((IP_Adress, Port))
        print(self.Axis + ' Socket created')

        self.initialize()
        self.calcSIUnitFactor()
        
        
        #self.sendCommand(bytearray([0, 0, 0, 0, 0, 14, 0, 43, 13, 1, 0, 0, 96, 146, 2, 0, 0, 0, 1, 1]))
        # Read the feed rate from the D1 and convert it to integer [mm]
        #self.feed_rate=(int.from_bytes(self.sendCommand(self.feedrate_array)[19:],byteorder='little'))/self.SI_unit_factor

    def initialize(self):
        # Aufruf der Funktion sendCommand zum hochfahren der State Machine mit vorher definierten Telegrammen (Handbuch: Visualisieung State Machine)
        # Call of the function sendCommand to start the State Machine with the previously defined telegrams (Manual: Visualisation State Machine)
        self.sendCommand(self.status_array)
        self.sendCommand(self.shutdown_array)
        self.sendCommand(self.status_array)
        self.sendCommand(self.switchOn_array)
        self.sendCommand(self.status_array)
        self.sendCommand(self.enableOperation_array)

    def sendCommand(self, data):
        self.s.send(data)
        res = self.s.recv(24)
        return list(res)
    
    def requestStatus(self):
        return self.sendCommand(self.status_array)

    def setMode(self, mode):
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 14, 0, 43, 13, 1, 0, 0, 96, 96, 0, 0, 0, 0, 1, mode]))
        while self.sendCommand(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 97, 0, 0, 0, 0, 1])) !=  [0, 0, 0, 0, 0, 14, 0, 43, 13, 0, 0, 0, 96, 97, 0, 0, 0, 0, 1, mode]:
            print('wait for mode')
            time.sleep(0.1)

#Shutdown Controlword senden und auf das folgende Statuswort pruefen. Pruefung auf mehrer Statuswords da mehrere Szenarien siehe Bit assignment Statusword, data package im Handbuch
#sending Shutdown Controlword and check the following Statusword. Checking several Statuswords because of various options. look at Bit assignment Statusword, data package in user manual
    def setShutDown(self):
        self.sendCommand(self.reset_array)
        self.sendCommand(self.shutdown_array)
        while (self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 33, 6]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 33, 22]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 33, 2]):
            print("wait for SHUT DOWN")
            time.sleep(1)

#Switch on Disabled Controlword senden und auf das folgende Statuswort pruefen. Pruefung auf mehrer Statuswords da mehrere Szenarien siehe Bit assignment Statusword, data package im Handbuch
#sending Switch on Disabled Controlword and check the following Statusword. Checking several Statuswords because of various options. look at Bit assignment Statusword, data package in user manual
    def setSwitchOn(self):
        self.sendCommand(self.switchOn_array)
        while (self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 35, 6]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 35, 22]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 35, 2]):
            print("wait for SWITCH ON")

            time.sleep(1)

#Operation Enable Controlword senden und auf das folgende Statuswort pruefen. Pruefung auf mehrer Statuswords da mehrere Szenarien siehe Bit assignment Statusword, data package im Handbuch
#Operation Enable Controlword and check the following Statusword. Checking several Statuswords because of various options. look at Bit assignment Statusword, data package in user manual
    def setEnableOperation(self):
        self.sendCommand(self.enableOperation_array)
        while (self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 6]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 2]):
            print("wait for OPERATION ENABLE")

            time.sleep(1)
            
    def readDigitalInput(self):
        return self.sendCommand(self.DInputs_array)
            
    def stopMovement(self):
        self.sendCommand(self.stop_array)
        print("Movement is stopped")


    def checkError(self):
        if (self.sendCommand(self.status_array) == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 22]
                or self.sendCommand(self.status_array) == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 6]
                or self.sendCommand(self.status_array) == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 34]
                or self.sendCommand(self.status_array) == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 2]):

            self.error = 1
        else:
            self.error = 0
        
    def get_actual_velocity(self):
        ans_velocity = self.sendCommand(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 108, 0, 0, 0, 0, 4]))
        act_velocity = abs(int.from_bytes(ans_velocity[19:], byteorder='little',signed=True) / self.SI_unit_factor)
        #print("\n"+self.Axis +' actual velo: '+str(act_velocity))
        
        return act_velocity
        
    def get_actual_position(self):
        ans_position = self.sendCommand(bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 100, 0, 0, 0, 0, 4]))
        act_position = int.from_bytes(ans_position[19:], byteorder='little') / self.SI_unit_factor
        self.position = act_position
        return act_position
        
    def calcSIUnitFactor(self):
        ans_position = self.sendCommand(self.SI_unit_array)
        ans_motion_method = int.from_bytes(ans_position[21:22], byteorder='big')
        ans_position_scale = int.from_bytes(ans_position[22:], byteorder='little')
        #if ==1, the method of motion linear is set
        if(ans_motion_method == 1):
            #if the smaller than 5, the factor is to scale up
            if(ans_position_scale > 5):
                self.SI_unit_factor = (10 ** -3)/(10**(ans_position_scale - 256))
            #if the bigger than 5, the factor is to scale down
            if(ans_position_scale < 5):
                self.SI_unit_factor = (10 ** -3)/(10 ** (ans_position_scale))
        # if ==65, the method of motion linear is set
        if(ans_motion_method == 65):
            if(ans_position_scale > 5):
                self.SI_unit_factor = (10** (-1 * (ans_position_scale - 256)))
            if(ans_position_scale < 5):
                self.SI_unit_factor = (10** (-1 * ans_position_scale))
        #print("SIUnit scale: "+ str(ans_position_scale))
        return self.SI_unit_factor


    def convertToFourByte(self, x):
        x = int(self.SI_unit_factor * x)
        byte_list = [0,0,0,0]
        if x >= 0 and x < 256 :
            byte_list[0] = x
        if x >= 256 and x < 65536:
            byte_list[1] = int(x/256)
            byte_list[0] = int(x%256)
        if x >= 65536 and x < 16777216:
            byte_list[2] = int(x / m.pow(256, 2))
            byte_list[1] = int((x - (byte_list[2]*m.pow(256,2))) / 256)
            byte_list[0] = int(x - (((byte_list[2]*m.pow(256,2)) + (byte_list[1]*256))))
        if x >= 16777216 and x < 4294967296:
            byte_list[3] = int(x / m.pow(256, 3))
            byte_list[2] = int((x - byte_list[3]*m.pow(256, 3)) / m.pow(256, 2))
            byte_list[1] = int(((x - byte_list[3]*m.pow(256, 3))-(byte_list[2]*m.pow(256,2))) / 256)
            byte_list[0] = int(x - ((byte_list[3]*m.pow(256, 3))+(byte_list[2]*m.pow(256, 2))+ (byte_list[1]*256)))
        return byte_list
        
        
    def homing(self, velo, acc):
    #6060h Modes of Operation
    #Set Homing mode (see "def set_mode(mode):"; Byte 19 = 6)
        self.setMode(6)
        self.sendCommand(self.enableOperation_array)
        
    # 6083h Profile Acceleration
    # Setzen der Beschleunigung auf 150 U/min² (Byte 19 = 16; Byte 20 = 39; Byte 21 = 0; Byte 22 = 0)
    # Set acceleration to 500 rpm/min² (Byte 19 = 80; Byte 20 = 195; Byte 21 = 0; Byte 22 = 0)
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, 152, 58, 0, 0]))


    # 6083h Profile Acceleration
    # Setzen der Beschleunigung auf 150 U/min² (Byte 19 = 16; Byte 20 = 39; Byte 21 = 0; Byte 22 = 0)
    # Set acceleration to 500 rpm/min² (Byte 19 = 80; Byte 20 = 195; Byte 21 = 0; Byte 22 = 0)
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, 152, 58, 0, 0]))
  
    # 6092h_01h Feed constant Subindex 1 (Feed) 
    #Set feed constant to 5400 (axis in Video); refer to manual (Byte 19 = 24; Byte 20 = 21; Byte 21 = 0; Byte 22 = 0)
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 0, 43, 13, 1, 0, 0, 96, 146, 1, 0, 0, 0, 4, 24, 21, 0, 0]))
    # 6092h_02h Feed constant Subindex 2 (Shaft revolutions)
    #Set shaft revolutions to 1; refer to manual (Byte 19 = 1; Byte 20 = 0; Byte 21 = 0; Byte 22 = 0)
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 0, 43, 13, 1, 0, 0, 96, 146, 2, 0, 0, 0, 4, 1, 0, 0, 0]))
        
        
        velo_byte_list = self.convertToFourByte(velo)

        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 153, 1, 0, 0, 0, 4, velo_byte_list[0], velo_byte_list[1], velo_byte_list[2], velo_byte_list[3]]))
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 153, 2, 0, 0, 0, 4, velo_byte_list[0], velo_byte_list[1], velo_byte_list[2], velo_byte_list[3]]))

            
        acc_byte_list = self.convertToFourByte(acc)

        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 154, 0, 0, 0, 0, 4, acc_byte_list[0], acc_byte_list[1], acc_byte_list[2], acc_byte_list[3]]))
        
    # 6040h Controlword
    #Start Homing
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 31, 0]))
        
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 0]))
        
        print("\nWait Homing", end='')
        while (self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]
            and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 6]
            and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 34]
            and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 2]):
            time.sleep(0.01)
            print (".", end='')
        print("\n"+self.Axis+"Homing finisched")


    def profile_position_mode(self, velo, acc, posi):
    # 6060h Modes of Operation
    # Set Homing mode (Byte 19 = 6)
        self.setMode(1)
        self.sendCommand(self.enableOperation_array)

    # 6081h Profile Velocity

        velo_list = self.convertToFourByte(velo)

        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 129, 0, 0, 0, 0, 4, velo_list[0], velo_list[1], velo_list[2], velo_list[3]]))
    # 6083h Profile Acceleration
    # Setzen der Beschleunigung auf 150 U/min² (Byte 19 = 16; Byte 20 = 39; Byte 21 = 0; Byte 22 = 0)
    # Set acceleration to 150mm/s2 
       
        acc_list = self.convertToFourByte(acc)
            
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, acc_list[0], acc_list[1], acc_list[2], acc_list[3]]))
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 132, 0, 0, 0, 0, 4, acc_list[0], acc_list[1], acc_list[2], acc_list[3]]))
    # 607A Target Position
    # Setzen sie einer Zielposition auf den Wert 150 mm (Byte 19 = 0; Byte 20 = 0; Byte 21 = 0; Byte 22 = 0)
    # Set target position to 0mm (Byte 19 = 0; Byte 20 = 0; Byte 21 = 0; Byte 22 = 0)

        posi_list = self.convertToFourByte(posi)
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 122, 0, 0, 0, 0, 4, posi_list[0], posi_list[1], posi_list[2], posi_list[3]]))
   
        
    # Startbefehl zur Bewegung des Motors über Bit 4
    # Set Bit 4 true to excecute the movoment of the motor
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 15, 1, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 31, 0]))
        
        time.sleep(0.1)

        while (self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 1, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]
                and self.sendCommand(self.status_array) != [0, 0, 0, 0, 0, 15, 1, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 22]):
            break
        
    def profile_velocity_mode(self, v_a_matrix):
        self.setMode(3)
        self.sendCommand(self.enableOperation_array)     
        # acceleration = 1000
        #self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, 160, 134, 1, 0]))
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 4, v_a_matrix[4], v_a_matrix[5], v_a_matrix[6], v_a_matrix[7]]))
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 132, 0, 0, 0, 0, 4, v_a_matrix[4], v_a_matrix[5], v_a_matrix[6], v_a_matrix[7]]))
        self.sendCommand(bytearray([0, 0, 0, 0, 0, 17, 1, 43, 13, 1, 0, 0, 96, 255, 0, 0, 0, 0, 4, v_a_matrix[0], v_a_matrix[1], v_a_matrix[2], v_a_matrix[3]]))
        
error = 0

X_Motor = Motor("169.254.0.1", 502, "X-Axis")
Y_Motor = Motor("169.254.0.2", 502, "Y-Axis")

factor = X_Motor.SI_unit_factor

X_Motor.homing(60,300)
Y_Motor.homing(60,300)

""" ******************** velocity curve ******************** """


def mod_velocity_curve(x):
    y = -5.83397691012945e-14 * pow(x, 9) + 4.01458396693356e-11 * pow(x, 8) - 9.62482037096911e-9 * pow(x, 7) + \
           1.06977262917339e-6 * pow(x, 6) - 5.68239363212274e-5 * pow(x, 5) + 0.00125022968775769 * pow(x, 4) - \
           0.0124822800434351 * pow(x, 3) + 0.531322885004075 * pow(x, 2) - 0.240497493514033 * x + 0.234808880863676
    return y / 2


""" ******************** position (mm) ******************** """


# get position of each interpolation point
def get_position_list(n, start_point, end_point):
    start_x = start_point[0]
    start_y = start_point[1]

    end_x = end_point[0]
    end_y = end_point[1]

    d_x = end_x - start_x
    d_y = end_y - start_y

    s_x = d_x / n  # n: sample number = segment number
    s_y = d_y / n

    p_list = []
    for i in range(n + 1):
        position = [round(start_x + i * s_x, 2), round(start_y + i * s_y, 2)]
        p_list.append(position)

    return p_list


""" ******************** velocity (mm/s) ******************** """


def get_velocity_list(n):  # finish
    v_list = []
    v_interval = 100 / n
    for i in range(n + 1):  # n+1 => symmetrical
        v_list.append(round(mod_velocity_curve(i * v_interval)))
    v_list[-1] = 0  # border condition
    return v_list


def get_xy_velocity_list(n, d_x, d_y):  # finish
    v_interval = 100 / n
    
    x_list = []
    y_list = []
    v_list = get_velocity_list(n)

    if d_x == 0:
        for v in v_list:
            x_list.append(0)
            y_list.append(v)
    elif d_y == 0:
        for v in v_list:
            x_list.append(v)
            y_list.append(0)
    else:
        deg = m.degrees(m.atan(d_y / d_x))
        for v in v_list:
            x_list.append(round(v * m.cos(m.radians(deg)), 2))
            y_list.append(round(v * m.sin(m.radians(deg)), 2))

    return x_list, y_list, v_list


""" ******************** time (s) ******************** """


def get_time_list(d, sample_num, v_list):
    s = d / (len(v_list) - 1)
    t_list = [0] * len(v_list)
    for i in range(1, len(v_list)):
        v = (v_list[i - 1] + v_list[i]) / 2
        t_list[i] = s / v
    return t_list


""" ******************** acceleration (mm^2/s) ******************** """


def get_acceleration_list(t_list, v_list):
    a_list = [0]
    for i in range(1, len(v_list)):
        dv = abs(v_list[i] - v_list[i - 1])
        dt = t_list[i]
        a_list.append(round(dv / dt))
    return a_list


""" ******************** to_byte ******************** """


def to_byte(x):  # finish
    return list(int(x * factor).to_bytes(4, byteorder='little', signed=True))


def neg_to_byte(num):  # check negative num 23.02
    byte_list = to_byte(abs(num))
    for i in range(4):
        byte_list[i] = 255 - byte_list[i]
    return byte_list


def v_to_byte(velo_list, forward):  # finish
    row = len(velo_list)
    velo_mat = np.arange(row * 4).reshape(row, 4)
    
    for i in range(0, row):
        if forward:
            velo_mat[i] = neg_to_byte(velo_list[i])
        else:
            velo_mat[i] = to_byte(velo_list[i])
    
    velo_mat[0] = [0, 0, 0, 0]
    velo_mat[row-1] = [0,0,0,0]

    return velo_mat


def a_to_byte(acc_list):  # finish
    row = len(acc_list)
    acc_mat = np.arange(row * 4).reshape(row, 4)
    for i in range(0, row):
        acc_mat[i] = to_byte(abs(acc_list[i]))
    return acc_mat


def conVeloAccMat(velo_mat, acc_mat):
    return np.hstack((velo_mat, acc_mat))


def calcNewCycleList(t_x_list, t_y_list):
    t_n_list = [None]*len(t_x_list)
    for i in range(0, len(t_x_list)):
        t_n_list[i] = 0.5*(t_x_list[i]+t_y_list[i])
    return t_n_list


def opCycleList(c_list):
    for i in range(1,len(c_list)):
        c_list[i] = c_list[i]-0.016
    return c_list


def checkCycleList(c_list):
    for c in c_list:
        if c < 0:
            print("\n\033[1;31m Warning!:\033[0m executive time < 0")


def showCycleDiff(t_list):
    t_diff_list = [None]*(len(t_list)-1)
    for i in range(0, len(t_diff_list)):
        t_diff_list[i] = abs(t_list[i+1] - t_list[i])


def get_list(n, start_point, end_point):
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
    
        time_n_list = calcNewCycleList(t_x_list, t_y_list)

        v_x_byte = v_to_byte(v_x_list, forward_x)
        v_y_byte = v_to_byte(v_y_list, forward_y)
        
        a_x_byte = a_to_byte(a_x_list)
        a_y_byte = a_to_byte(a_y_list)
        
        v_a_x_byte = conVeloAccMat(v_x_byte, a_x_byte)
        v_a_y_byte = conVeloAccMat(v_y_byte, a_y_byte)

        op_time_n_list = opCycleList(time_n_list)

    if d_y == 0.0:
        v_x_list = get_velocity_list(n)
        v_y_list = [0] * len(v_x_list)
        v_list = v_x_list
        
        t_x_list = get_time_list(d_x, n, v_x_list)
        a_x_list = get_acceleration_list(t_x_list, v_x_list)
        
        v_x_byte = v_to_byte(v_x_list, forward_x)
        a_x_byte = a_to_byte(a_x_list)

        v_a_x_byte = conVeloAccMat(v_x_byte, a_x_byte)
        v_a_y_byte = []

        time_n_list = t_x_list

        op_time_n_list = opCycleList(time_n_list)

    if d_x == 0.0:
        v_y_list = get_velocity_list(n)
        v_x_list = [0] * len(v_y_list)
        v_list = v_y_list

        t_y_list = get_time_list(d_y, n, v_y_list)
        a_y_list = get_acceleration_list(t_y_list, v_y_list)
        
        v_y_byte = v_to_byte(v_y_list, forward_y)
        a_y_byte = a_to_byte(a_y_list)

        v_a_y_byte = conVeloAccMat(v_y_byte, a_y_byte)
        v_a_x_byte = []

        time_n_list = t_y_list
        op_time_n_list = opCycleList(time_n_list)

    checkCycleList(op_time_n_list)

    return v_x_list, v_y_list, v_list, v_a_x_byte, v_a_y_byte, op_time_n_list

v_x = []
v_y = []

def move(start_point, end_point, v_a_x_mat, v_a_y_mat):
    start_x = start_point[0]
    start_y = start_point[1]
    end_x = end_point[0]
    end_y = end_point[1]

    d_x = end_x - start_x
    d_y = end_y - start_y
    
    p_list = get_position_list(sample_num, start_point, end_point)
    
    if d_x != 0.0 and d_y != 0.0:
        for i in range(1, sample_num + 1):
            v_x.append(X_Motor.get_actual_velocity())
            v_y.append(Y_Motor.get_actual_velocity())
            
            X_Motor.profile_velocity_mode(v_a_x_mat[i])
            Y_Motor.profile_velocity_mode(v_a_y_mat[i])
#             time.sleep(time_list[i])
            
            p_x = p_list[i][0]
            p_y = p_list[i][1]
            
            if d_x >= 0 and d_y >= 0:
                print("+, +")
                while X_Motor.get_actual_position() < p_x and Y_Motor.get_actual_position() < p_y: 
                    position_condition(10, end_x, end_y)
            elif d_x < 0 and d_y >= 0:
                print("-, +")
                while X_Motor.get_actual_position() > p_x and Y_Motor.get_actual_position() < p_y:
                    position_condition(10, end_x, end_y)
            elif d_x >= 0 and d_y < 0:
                print("+, -")
                while X_Motor.get_actual_position() < p_x and Y_Motor.get_actual_position() > p_y:
                    position_condition(10, end_x, end_y)
            elif d_x < 0 and d_y < 0:
                print("-,-")
                while X_Motor.get_actual_position() > p_x and Y_Motor.get_actual_position() > p_y:
                    position_condition(10, end_x, end_y)
        
        print("Stop Position: " + str(X_Motor.get_actual_position()) + ", " + str(Y_Motor.get_actual_position()))

    if d_x != 0.0 and d_y == 0.0:
        for i in range(1, sample_num + 1):
            X_Motor.profile_velocity_mode(v_a_x_mat[i])
            
            p_x = p_list[i][0]
            
            if d_x >= 0:
                print("+x")
                while X_Motor.get_actual_position() < p_x:
                    if abs(X_Motor.get_actual_position() - end_x) <= 20:
                        X_Motor.profile_position_mode(100, 100, end_x)
            elif d_x < 0:
                print("-x")
                while X_Motor.get_actual_position() > p_x:
                    if abs(X_Motor.get_actual_position() - end_x) <= 20:
                        X_Motor.profile_position_mode(100, 100, end_x)
                
        print("Stop Position: " + str(X_Motor.get_actual_position()) + ", " + str(Y_Motor.get_actual_position()))

    if d_x == 0.0 and d_y != 0.0:
        for i in range(1, sample_num + 1):
            Y_Motor.profile_velocity_mode(v_a_y_mat[i])
            
            p_y = p_list[i][1]
            
            if d_y >= 0:
                print("+y")
                while Y_Motor.get_actual_position() < p_y:
                    if abs(Y_Motor.get_actual_position() - end_y) <= 20:
                        Y_Motor.profile_position_mode(100, 100, end_y)
            elif d_y < 0:
                print("-y")
                while Y_Motor.get_actual_position() > p_y:
                    if abs(Y_Motor.get_actual_position() - end_y) <= 20:
                        Y_Motor.profile_position_mode(100, 100, end_y)
                        
        print("Stop Position: " + str(X_Motor.get_actual_position()) + ", " + str(Y_Motor.get_actual_position()))


def position_condition(distance, end_x, end_y):
    if abs(X_Motor.get_actual_position() - end_x) <= distance and abs(Y_Motor.get_actual_position() - end_y) <= distance:
        print("End Position: " + str(end_x) + ", " + str(end_y))
        X_Motor.profile_position_mode(100, 100, end_x)
        Y_Motor.profile_position_mode(100, 100, end_y)
    time.sleep(0.01)


def direction(start, end):
    return True if start >= end else False


""" ******************** velocity curve end ******************** """


def calcLoosenModeTarget(max_angle, step_angle, position_a):
    steps = m.ceil(max_angle/step_angle)+1
    
    target_x_list = [0]*steps
    target_y_list = [0]*steps
    temp_angle = step_angle
    
    target_x_list[0] = int(position_a)
    target_y_list[0] = int(250)
    
    for i in range(1, steps):
        target_x_list[i] = 250-round(m.cos(m.radians(temp_angle))*position_a)
        target_y_list[i] = 250-round(m.sin(m.radians(temp_angle))*position_a)
        temp_angle = temp_angle + step_angle
    
    if debug == True:
        print("\nTarget x list:")
        print(target_x_list)
        print("\nTarget y list")
        print(target_y_list)
    
    return target_x_list, target_y_list


def calcLoosenModeVeloList(target_x_list, target_y_list, velo):
    diff_x_list = [0]*len(target_x_list)
    diff_y_list = [0]*len(target_y_list)
    diff_x_list[0] = 0
    diff_y_list[0] = 0
    
    for i in range(1, len(diff_x_list)):
        diff_x_list[i] = abs(target_x_list[i]-target_x_list[i-1])
        diff_y_list[i] = abs(target_y_list[i]-target_y_list[i-1])
        
    diff_x_list = diff_x_list[1:]
    diff_y_list = diff_y_list[1:]
    
    if debug == True:    
        print("\nlm x difference:")
        print(diff_x_list)
        print("\nlm y difference:")
        print(diff_y_list)
    
    v_x_list = [0]*len(diff_x_list) 
    v_y_list = [0]*len(diff_y_list)
    
    start_x = abs(target_x_list[-1] - target_x_list[0])
    start_y = abs(target_y_list[-1] - target_y_list[0])
    
    if start_x > start_y:
        temp_slow = diff_x_list
        temp_fast = diff_y_list
    else:
        temp_slow = diff_y_list
        temp_fast = diff_x_list
    
    temp_t_list = [0]*len(v_x_list)
    
    for i in range(0, len(temp_t_list)):
        temp_t_list[i] = temp_slow[i] / velo
    
    for i in range(0,len(v_x_list)):
        v_x_list[i] = int(diff_x_list[i]/temp_t_list[i])
        v_y_list[i] = int(diff_y_list[i]/temp_t_list[i])
    
    if debug == True:
        print("\nlm x velo:")
        print(v_x_list)
        print("\nlm y velo:")
        print(v_y_list)
        
    return v_x_list, v_y_list
        

def loosenMode(target_x_list, target_y_list, frequency, v_x_list, v_y_list, position_a):
    X_Motor.profile_position_mode(100, 150, lm_target_x_list[0])
    Y_Motor.profile_position_mode(100, 150, lm_target_y_list[0])
    while((X_Motor.get_actual_velocity() != 0) or (Y_Motor.get_actual_velocity() != 0)):
        time.sleep(0.2)
    
    for i in range(1, len(target_x_list)):
        for j in range(0, frequency):
            X_Motor.profile_position_mode(v_x_list[i-1],4000, target_x_list[i])
            Y_Motor.profile_position_mode(v_y_list[i-1],4000, target_y_list[i])
            while((X_Motor.get_actual_velocity() != 0) and (Y_Motor.get_actual_velocity() != 0)):
                time.sleep(0.2)
            X_Motor.profile_position_mode(v_x_list[i-1], 4000, target_x_list[i-1])
            Y_Motor.profile_position_mode(v_y_list[i-1], 4000, target_y_list[i-1])
            while((X_Motor.get_actual_velocity() != 0) and (Y_Motor.get_actual_velocity() != 0)):
                time.sleep(0.2)
                
        X_Motor.profile_position_mode(v_x_list[i-1], 4000, target_x_list[i])
        Y_Motor.profile_position_mode(v_y_list[i-1], 4000, target_y_list[i])
        while((X_Motor.get_actual_velocity() != 0) or (Y_Motor.get_actual_velocity() != 0)):
            time.sleep(0.2)            
    
    #Y_Motor.homing(60, 300)
    #X_Motor.profile_position_mode(100, target_x_list[0])
    #while((X_Motor.get_actual_velocity() != 0) or (Y_Motor.get_actual_velocity() != 0)):
    #    time.sleep(0.2)
# Num of interpolation points
sample_num = 20

# Target Distance of x/y for test
d_x = 200.0
d_y = 200.0

start_x = 0.0
start_y = 0.0
target_x = abs(start_x - d_x)
target_y = abs(start_y - d_y)

forward_x = True
forward_y = False

forward_x = direction(start_x, target_x)
forward_y = direction(start_y, target_y)

act_posi_x = X_Motor.get_actual_position()
act_posi_y = Y_Motor.get_actual_position()

# Target 
dist_t = m.sqrt((d_x**2)+(d_y**2))

(velo_x_list, velo_y_list, v_list, velo_acc_x_mat, velo_acc_y_mat, op_time_n_list) = get_list(sample_num, [start_x, start_y], [target_x, target_y])

real_time_list = [None]*(len(velo_x_list))
#real_time_index = 1

real_x_velo_array = np.empty(sample_num+1)
real_x_posi_array = np.empty(sample_num+1)
real_y_velo_array = np.empty(sample_num+1)
real_y_posi_array = np.empty(sample_num+1)
real_x_velo_array[0] = 0
real_y_velo_array[0] = 0
real_x_posi_array[0] = start_x
real_y_posi_array[0] = start_x

shoulder_width = 200.0

max_angle = 60
step_angle = 20
frequency = 3
velo_c = 20


### HANDEINHEIT
os.system("sudo ifconfig can0 down") 
os.system("sudo /sbin/ip link set can0 up type can bitrate 125000")
os.system("sudo ifconfig can0 up")    
    
        
network=canopen.Network()
network.connect(channel='can0', bustype='socketcan', bitrate=125000)

node_1 = hand.Drive(network, 127)
node_2 = hand.Drive(network, 126)


cycle = 1
target_velo_1 = 0x14
target_velo_2 = 0x14


frame_hand_setup = [[sg.Text('Drive 1',size=(28,2), font="Any 20"), sg.Text('Drive 2',size=(14,2), font="Any 20")],
               [sg.Text('Start point 1:',size=(11,2), font="Any 20"),
                sg.Text(node_1.start_position, size=(7,2), font="Any 20", key="start_posi_1"),
                sg.Button("set", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="set_start_1"),
                sg.Text('Start point 2:', size=(11,2),font="Any 20"),
                sg.Text(node_2.start_position, size=(7,2), font="Any 20", key="start_posi_2"),
                sg.Button("set", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="set_start_2")
               ],
               [sg.Text('End point 1:',size=(11,2), font="Any 20"),
                sg.Text(node_1.end_position, size=(7,2), font="Any 20", key="end_posi_1"),
                sg.Button("set", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="set_end_1"),
                sg.Text('End point 2:',size=(11,2), font="Any 20"),
                sg.Text(node_2.end_position, size=(7,2), font="Any 20", key="end_posi_2"),
                sg.Button("set", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="set_end_2"),
               ],
               [sg.Text("Distance 1:",size=(11,2), font="Any 20"),
                sg.Text(node_1.distance, size=(16,2), font="Any 20", key="distance_1"),
                sg.Text("Distance 2:",size=(11,2), font="Any 20"),
                sg.Text(node_2.distance, size=(7,2), font="Any 20", key="distance_2")
               ],
               [sg.Text("Velocity 1 [mm/s]: ",size=(11,2),font="Any 20"), sg.Input(target_velo_1, size=(7,2), font="Any 20", key ="velo_1"),
                sg.Button("save", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="velo_save_1"),
                sg.Text("Velocity 2 [mm/s]: ",size=(11,2),font="Any 20"), sg.Input(target_velo_2, size=(7,2), font="Any 20", key ="velo_2"),
                sg.Button("save", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="velo_save_2")
               ],
               [sg.Text("Cycle: ",font="Any 20"), sg.Input(cycle, size=(7,2), font="Any 20", key ="cycle"),
                sg.Button("save", size=(7,2), font = "Any 20", button_color = ("white", "grey"), key="cycle_save")
               ]
             ]

frame_drive = [[sg.Text("Power: ",size=(14,2), font="Any 20"),
                sg.Button("ON", size=(7,2), font="Any 20", button_color=("white","green")),
                sg.Button("OFF", size=(7,2), font="Any 20", button_color=("white","red"))],
               [sg.Text("Homing Mode: ", size=(14,2), font="Any 20"),
                sg.Button("Homing 1", size=(7,2), font="Any 20", button_color=("white","grey")),
                sg.Button("Homing 2", size=(7,2), font="Any 20", button_color=("white","grey"))],
               [sg.Text("Repetition Mode:", size=(14,2), font="Any 20"),
                sg.Button("Start", size=(7,2), font="Any 20", button_color=("white","black"), key="node_start"),
                sg.Button("Stop", size=(7,2), font="Any 20", button_color=("white","black"), key="node_stop")]
              ]

frame_hand_info = [[sg.Text("Actual Position:",size=(14,2), font="Any 20")],
              [sg.Text("Drive 1: ",size=(7,2), font="Any 20"), sg.Text(node_1.getActualPosition()*node_1.posi_factor,size=(7,2), font="Any 20", key="act_posi_1")],
              [sg.Text("Drive 2: ",size=(7,2), font="Any 20"), sg.Text(node_2.getActualPosition()*node_2.posi_factor,size=(7,2), font="Any 20", key="act_posi_2")],
              [sg.Button("Update",size=(14,2), font = "Any 20",button_color=("white","grey"))]
             ]


hand_window_layout = [
                [sg.Frame("Set Up", frame_hand_setup, font="Any 20", title_color='black')],
                [sg.Frame("Drive", frame_drive, font="Any 20", title_color='black'),sg.Push(), sg.Frame("Info", frame_hand_info,font="Any 20", title_color='black'),sg.Push()],
                
                ]

# All the stuff inside your window.

frame_cp = [[sg.Text("Control Point Mode",size=(20, 2), font="Any 20")],
            [sg.Text('Shoulder width:',size=(14, 2), font="Any 20"), sg.InputText(shoulder_width, size=(7,2), font="Any 20", key='shoulder_width')],
            [sg.Text("Control point : ", size=(14, 2), font="Any 20"), sg.Combo(values=['', 1, 2, 3, 4, 5,6], font="Any 20", key="control_point")],
            [sg.Text("", size=(14, 2), font="Any 20")],
            [sg.Text("", size=(14, 2), font="Any 20")],
            [sg.Button("save", size=(7, 2), font="Any 20", key="sw_save"),
             sg.Button("Start", size=(14, 2), font="Any 20", button_color=('white', 'green'), key="CP_Start"),
             sg.Button("Stop", size=(14, 2), font="Any 20", button_color=('white', 'red'))],
           ]

frame_pv = [[sg.Text("Profil Position Mode:",size=(20, 2), font="Any 20")],
            [sg.Text("Motor X",size=(26, 2), font="Any 20"), sg.Text("Motor Y",size=(14, 2), font="Any 20")],
            [sg.Text("Start Position x: ",size=(14, 2), font="Any 20"), sg.InputText(start_x, size=(7,2), font="Any 20", key="start_x"),
             sg.Text("Start Position y: ",size=(14, 2), font="Any 20"), sg.InputText(start_y, size=(7,2), font="Any 20", key="start_y")],
            [sg.Text("Target Position x: ",size=(14, 2), font="Any 20"), sg.InputText(target_x, size=(7,2), font="Any 20", key="target_x"),
             sg.Text("Target Position y: ",size=(14, 2), font="Any 20"), sg.InputText(target_y, size=(7,2), font="Any 20", key="target_y")],
            [sg.Text("", size=(14, 2), font="Any 20")],
            [sg.Button("save", size=(7,2), font="Any 20", key="v_save"),
             sg.Button('Start',size=(14,2), font="Any 20",button_color=('white', 'green'), key="V_Start"),
             #sg.Button("Plot", size=(14, 2), font="Any 20", button_color=('white', 'grey80')),sg.Button('data_save',size=(14,2), font="Any 20",button_color=('white', 'grey80'))
             sg.Button("Stop", size=(14, 2), font="Any 20", button_color=('white', 'red'))
            ]
           ]

frame_rm = [[sg.Text("Relax Mode",size=(14, 2), font="Any 20")],
            [sg.Text("Max.Angle[deg.]:",size=(20, 2), font="Any 20"), sg.InputText(max_angle, size=(7,2), font="Any 20", key="max_angle")],
            [sg.Text("Step[deg.]:",size=(20, 2), font="Any 20"), sg.InputText(step_angle, size=(7,2), font="Any 20", key="step_angle")],
            [sg.Text("Frequency:",size=(20, 2), font="Any 20"), sg.InputText(frequency, size=(7,2), font="Any 20", key="frequency")],
            [sg.Text("Velocity:",size=(20, 2), font="Any 20"), sg.InputText(velo_c, size=(7,2), font="Any 20", key="velo_c")],
            [sg.Button("save", size=(7, 2), font="Any 20", key="a_save"),
             sg.Button('Start', size=(14,2), font="Any 20",button_color=('white', 'green'), key="A_Start"),
             sg.Button("Stop", size=(14, 2), font="Any 20", button_color=('white', 'red'))
            ]
           ]

frame_arm_info = [[sg.Text("Actual Position: ", size=(14,2), font="Any 20")],
                  [sg.Text("Motor X: ", size=(7,2), font="Any 20"), sg.Text(act_posi_x, size=(7,2), font="Any 20", key="act_posi_x")],
                  [sg.Text("Motor Y: ", size=(7,2), font="Any 20"), sg.Text(act_posi_y, size=(7,2), font="Any 20", key="act_posi_y")],
                  [sg.Button("Update", size=(14, 2), font="Any 20", button_color=('white', 'grey80'))]]


frame_motor = [[sg.Text("Homing Mode", size=(14,2), font="Any 20"), sg.Button("Homing",size=(14, 2), font="Any 20", button_color=('white', 'grey80'))],
               [sg.Text("Interface: ", size=(14,2), font="Any 20"), sg.Button('Open',size=(14,2), font="Any 20")]
              ]

mode_tab = [[sg.TabGroup([[sg.Tab('Contol\nPoint', frame_cp, font="Any 20"),sg.Tab('Profil\nPosition', frame_pv, font="Any 20"),sg.Tab('Relax',frame_rm, font="Any 20")]],tab_location='lefttop')]]


arm_window_layout = [[sg.Frame('Set Up', mode_tab, font="Any 20", title_color='black')],
                     [sg.Frame('Motor', frame_motor, font="Any 20", title_color='black'), sg.Push(), sg.Frame("Info", frame_arm_info,font="Any 20", title_color='black'),sg.Push()]
                    ]

window_layout = [[sg.TabGroup([[sg.Tab('Arm', arm_window_layout), sg.Tab('Hand', hand_window_layout)]],tab_location='topleft')],
                 [sg.Push(), sg.Button("Quit", size=(14,2), font = "Any 20", button_color = ("white", "orange"))]
                ]

window = sg.Window('ArmRehaGeraet', window_layout, grab_anywhere=True)


def updateActPosition():
    act_posi_x = X_Motor.get_actual_position()
    act_posi_y = Y_Motor.get_actual_position()
    window['act_posi_x'].update(act_posi_x)
    window['act_posi_y'].update(act_posi_y)

# Event Loop to process "events" and get the "values" of the inputs

column_index = 0

""" ********** 17.02.2023 ********** """

real_v_x_list = []  # real velocity
real_v_y_list = []
real_p_x_list = []  # real position
real_p_y_list = []
real_t_list = []

def clear_info():
    real_v_x_list.clear()
    real_v_y_list.clear()
    real_p_x_list.clear()
    real_p_y_list.clear()
    real_t_list.clear()
    
def save_info():
    real_v_x_list.append(X_Motor.get_actual_velocity())
    real_v_y_list.append(Y_Motor.get_actual_velocity())
    real_p_x_list.append(X_Motor.get_actual_position())
    real_p_y_list.append(Y_Motor.get_actual_position())
    real_t_list.append(time.time())
    
""" ********** 17.02.2023 ********** """


while True:
    event, values = window.read()
    if event in (None, 'Quit'):
        X_Motor.profile_position_mode(80, 80, 245)
        Y_Motor.profile_position_mode(80, 80, 245)
        while(X_Motor.get_actual_position()<240.0 or Y_Motor.get_actual_position()<240.0):
            time.sleep(0.02)
            
        X_Motor.homing(60,300)
        Y_Motor.homing(60,300)
        
        node_1.switchOff()
        node_2.switchOff() 
        
        break

    X_Motor.checkError()
    Y_Motor.checkError()

    if X_Motor.error == 0 and Y_Motor.error == 0 :
        error = 0
    else:
        error = 1

#Wenn kein Fehler start der Initialisierung
#If no Error is up start the initialisierung
    if error == 0:
        time.sleep(0.5)
        while error == 0:
            if event in (None, 'Quit'):
                #X_Motor.homing()
                #Y_Motor.homing()
                print("Quit")
                break

            if event in (None, 'Open'):
                webinterface=webbrowser.open('http://169.254.0.1/')
                webinterface1=webbrowser.open('http://169.254.0.2/')
                break

            if event in (None, 'Stop'):
                X_Motor.stopMovement()
                Y_Motor.stopMovement()
                break
            
            if event in (None, 'Update'):
                updateActPosition()
                act_position_x = X_Motor.get_actual_position()
                act_position_y = Y_Motor.get_actual_position()           
                break

            if event in (None, 'Homing'):
                X_Motor.profile_position_mode(80, 80, 245)
                Y_Motor.profile_position_mode(80, 80, 245)
                while(X_Motor.get_actual_position()<240.0 or Y_Motor.get_actual_position()<240.0):
                    time.sleep(0.02)
                X_Motor.homing(60,300)
                Y_Motor.homing(60,300)
                updateActPosition()
                break
            
            if event in (None, 'v_save'):
                start_x = float(values['start_x'])
                start_y = float(values['start_y'])
                target_x = float(values['target_x'])
                target_y = float(values['target_y'])
                
                window['start_x'].update(start_x)
                window['target_x'].update(target_x)
                window['start_y'].update(start_y)
                window['target_y'].update(target_y)
                    
                X_Motor.profile_position_mode(80, 80, start_x)
                Y_Motor.profile_position_mode(80, 80, start_y)
                print("start point: " + str(start_x) + ', '+ str(start_y))
                    
                d_x = abs(target_x - start_x)
                d_y = abs(target_y - start_y)
                dist_t = m.sqrt((d_x**2)+(d_y**2))
                
                (velo_x_list, velo_y_list, velo_c_list, velo_acc_x_mat, velo_acc_y_mat, op_time_n_list) = get_list(sample_num, [start_x, start_y], [target_x, target_y])
                real_time_list = [None]*(len(velo_x_list))

                break

            """ ********** 27.02.2023
            1. Armeinheit do not stop at homing point (350, 250), out of range (0,0) (350,250)
            2. every time must click the "save" then click "start" if not >> error
            3. does not support repeat movement
            4. wired point (0,0) (250,250), (240, 240), (250, 220)
            (250, 250) -> (0, 0)
            
            start point used profile position mode, so there isn't range limit
            only target point need to consider the range limit
            
            X safe range
            pos direction (0,0) -> (300,0) work
            neg direction (300,0) -> (50,0) work
            
            Y safe range
            pos direction (0,0) -> (0,220) work
            neg direction (0,250) -> (0,0) work
            
            (250, 250) -> (50, 50) work
            (350, 0) -> (80, 180) work
            
            (0,200) -> (300, 0) workss
            (0,250) -> (250, 0) no response
            (0,240) -> (200, 0) no response at (0, 240)
            (50,240) -> (200, 0) no response
            (50,200) -> (200, 0) work
            ********** """
            
            if event in (None, 'V_Start'):
                clear_info()
                real_time_list[0] = time.time()
                
                for i in range(3):
                    print("start point: " + str(start_x) + ', '+ str(start_y))
                    X_Motor.profile_position_mode(80, 80, start_x)
                    Y_Motor.profile_position_mode(80, 80, start_y)
                        
                    while X_Motor.get_actual_velocity() != 0 or Y_Motor.get_actual_velocity() != 0:
                        time.sleep(0.1)
                    
                    print("target point: " + str(target_x) + ', '+ str(target_y))
                    move([start_x, start_y], [target_x, target_y], velo_acc_x_mat, velo_acc_y_mat)
                    
                    updateActPosition()
                
                print(v_x)
                print(v_y)
                
                break
            
            """ ********** 27.02.2023 ********** """
            
            if event in (None, "Plot"):
                d_x = abs(target_x - start_x)
                d_y = abs(target_y - start_y)
                plot(d_x, d_y, start_x, start_y)
                
                break
            
            if event in (None, "data_save"):
                #notice: set libreoffice calc as default open app
                
                file_name = "test.xlsx"
                wb = xl.load_workbook(file_name)
                test_1 = wb["5"]
                test_2 = wb["10"]
                test_3 = wb["15"]
                test_4 = wb["20"]
                
                column = ["B","C","D","E","F","G","H","I","J","K"]
                
                real_v_t_array = np.zeros(len(real_x_velo_array))

                for i in range(0, len(real_v_t_array)):
                    real_v_t_array[i] = m.sqrt((real_x_velo_array[i]**2) + (real_y_velo_array[i]**2))
                
#                 if sample_num == 5:
#                     for i in range(0, len(velo_c_list)):
#                         # write target velo in A column
#                         test_1["A%d" % (i+2)].value = velo_c_list[i]
#                         # write real velo iterative in from 2. row downwards, and wrap column automatic 
#                         test_1["%s%d" %(column[column_index], i+2)].value = real_v_t_array[i]
#                     wb.save(file_name)
#                     
#                 if sample_num == 10:
#                     for i in range(0, len(velo_c_list)):
#                         test_2["A%d" % (i+2)].value = velo_c_list[i]
#                         test_2["%s%d" %(column[column_index], i+2)].value = real_v_t_array[i] 
#                     wb.save(file_name)
#                     
#                 if sample_num == 15:
#                     for i in range(0, len(velo_c_list)):
#                         test_3["A%d" % (i+2)].value = velo_c_list[i]
#                         test_3["%s%d" %(column[column_index], i+2)].value = real_v_t_array[i]
#                     wb.save(file_name)
#                     
#                 if sample_num == 20:
#                     for i in range(0, len(velo_c_list)):
#                         test_4["A%d" % (i+2)].value = velo_c_list[i]
#                         test_4["%s%d" %(column[column_index], i+2)].value = real_v_t_array[i]
#                     wb.save(file_name)
                
                print("\ndata saved")
                
                column_index = (column_index+1)%10

                break
            
            #if event in (None, "AuflockernMode"):
                
            if event in (None, "sw_save"):
                shoulder_width = float(values['shoulder_width'])
                window['shoulder_width'].update(shoulder_width)
                mp4_x = m.ceil(shoulder_width*0.5)
                mp4_y = m.ceil(shoulder_width*0.5)
                mp6_x = m.ceil(shoulder_width)
                mp6_y = m.ceil(shoulder_width)
                print("\nnew shoulder width: " + str(shoulder_width))
                break
            
            if event in (None, "a_save"):
                max_angle = int(values["max_angle"])
                step_angle = int(values["step_angle"])
                frequency = int(values["frequency"])
                velo_c = int(values["velo_c"])
                window["frequency"].update(frequency)
                (lm_target_x_list, lm_target_y_list) = calcLoosenModeTarget(max_angle, step_angle, mp5_x)
                (lm_velo_x_list, lm_velo_y_list) = calcLoosenModeVeloList(lm_target_x_list, lm_target_y_list, velo_c)
                time.sleep(0.1)
                X_Motor.profile_position_mode(100, 150, lm_target_x_list[0])
                Y_Motor.profile_position_mode(100, 150, lm_target_y_list[0])
                while((X_Motor.get_actual_velocity() != 0) or (Y_Motor.get_actual_velocity() != 0)):
                    time.sleep(0.2)
                break
            
            if event in (None, "A_Start"):
                loosenMode(lm_target_x_list, lm_target_y_list, frequency, lm_velo_x_list, lm_velo_y_list, mp5_x)
                updateActPosition()
                break

            if values["control_point"] != '':
                
                if values["control_point"]== 1 and event in (None, 'CP_Start') :
                    
                    dist_x = mp1_x
                    dist_y = mp1_y

                    X_Motor.setprofile_velocity_mode()
                    Y_Motor.setprofile_velocity_mode()
                    #if X_Motor.homing_completed == 1 and Y_Motor.homing_completed == 1:

                    move(mp1_x, mp1_y, mp1_x_velo_acc_mat, mp1_y_velo_acc_mat, mp1_op_time_n_list)

                    #else:
                    #    print("plese homing")
                        
                    updateActPosition()
                    break

                if values["control_point"]== 2 and event in (None, 'CP_Start') :
                    
                    dist_x = mp2_x
                    dist_y = mp2_y
                    
                    X_Motor.setprofile_velocity_mode()
                    Y_Motor.setprofile_velocity_mode()
                    if target_x <= 250.0 and target_x >= 0.0 and target_y <= 250.0 and target_y >= 0.0:

                        move(mp2_x, mp_x_velo_acc_mat, mp2_y_velo_acc_mat, mp2_op_time_n_list)

                    else:
                        print("plese homing")
                        
                    updateActPosition()
                    break

                if values["control_point"]== 3 and event in (None, 'CP_Start') :
                    
                    dist_x = mp3_x
                    dist_y = mp3_y
                    
                    X_Motor.setprofile_velocity_mode()
                    Y_Motor.setprofile_velocity_mode()
                    if target_x <= 250.0 and target_x >= 0.0 and target_y <= 250.0 and target_y >= 0.0:

                        move(mp3_x, mp3_y, mp3_x_velo_acc_mat, mp3_y_velo_acc_mat, mp3_op_time_n_list)

                    else:
                        print("plese homing")
                        
                    updateActPosition()
                    break

                if values["control_point"]== 4 and event in (None, 'CP_Start') :
                    
                    dist_x = mp4_x
                    dist_y = mp4_y
                    
                    X_Motor.setprofile_velocity_mode()
                    Y_Motor.setprofile_velocity_mode()
                    if target_x <= 250.0 and target_x >= 0.0 and target_y <= 250.0 and target_y >= 0.0:

                        move(mp4_x, mp4_y, mp4_x_velo_acc_mat, mp4_y_velo_acc_mat, mp4_op_time_n_list)

                    else:
                        print("plese homing")
                        
                    updateActPosition()
                    break

                if values["control_point"]== 5 and event in (None, 'CP_Start') :
                    
                    dist_x = mp5_x
                    dist_y = mp5_y
                    
                    X_Motor.setprofile_velocity_mode()
                    Y_Motor.setprofile_velocity_mode()
                    if target_x <= 250.0 and target_x >= 0.0 and target_y <= 250.0 and target_y >= 0.0:

                        move(mp5_x, mp5_y, mp5_x_velo_acc_mat, mp5_y_velo_acc_mat, mp5_op_time_n_list)

                    else:
                        print("plese homing")
                        
                    updateActPosition()
                    break

                if values["control_point"]== 6 and event in (None, 'CP_Start') :
                    
                    dist_x = mp6_x
                    dist_y = mp6_y
                    
                    X_Motor.setprofile_velocity_mode()
                    Y_Motor.setprofile_velocity_mode()
                    if target_x <= 250.0 and target_x >= 0.0 and target_y <= 250.0 and target_y >= 0.0:

                        move(mp6_x, mp6_y, mp6_x_velo_acc_mat, mp6_y_velo_acc_mat, mp6_op_time_n_list)

                    else:
                        print("plese homing")
                        

                    updateActPosition()
                    break
                
                
            if event in (None, "set_start_1"):
                node_1.start_position = node_1.getget_actual_position()
                window['start_posi_1'].update(node_1.start_position*node_1.posi_factor)
                node_1.distance = abs(node_1.end_position-node_1.start_position)
                window['distance_1'].update(node_1.distance*node_1.posi_factor)
                break
        
            if event in (None, "set_start_2"):
                node_2.start_position = node_2.getget_actual_position()
                window['start_posi_2'].update(node_2.start_position*node_2.posi_factor)
                node_2.distance = abs(node_2.end_position-node_2.start_position)
                window['distance_2'].update(node_2.distance*node_2.posi_factor)
                break
        
            if event in (None, "set_end_1"):
                node_1.end_position = node_1.getget_actual_position()
                window['end_posi_1'].update(node_1.end_position*node_1.posi_factor)
                node_1.distance = abs(node_1.end_position-node_1.start_position)
                window['distance_1'].update(node_1.distance*node_1.posi_factor)
                break
        
            if event in (None, "set_end_2"):
                node_2.end_position = node_2.getget_actual_position()
                window['end_posi_2'].update(node_2.end_position*node_2.posi_factor)
                node_2.distance = abs(node_2.end_position-node_2.start_position)
                window['distance_2'].update(node_2.distance*node_2.posi_factor)
                break
        
            if event in (None, "cycle_save"):
                cycle = int(values['cycle'])
                window['cycle'].update(cycle)
                break
            
            if event in (None, "velo_save_1"):
                target_velo_1 = int(values['velo_1'])
                node_1.setTargetVelo(target_velo_1)
            
                window['velo_1'].update(target_velo_1)
                break
        
            if event in (None, "velo_save_2"):
                target_velo_2 = int(values['velo_2'])
                node_2.setTargetVelo(target_velo_2)
            
                window['velo_1'].update(target_velo_1)
                break
        
            if event in (None, "ON"):
                node_1.switchOn()
                node_2.switchOn()
                break
            
            if event in (None, "OFF"):
                node_1.switchOff()
                node_2.switchOff()
                break
        
            if event in (None, "Homing 1"):
            
                node_1.switchOn()
            
                node_1.setHomingMode()
                node_1.homing()

                while(node_1.node.sdo[0x606c].raw != 0 and node_2.node.sdo[0x606c].raw != 0):
                    time.sleep(0.2)
                print("Homing finisched "+str(node_1.node.sdo[0x6041].bits[12]))
                print("Homing Fehler "+str(node_1.node.sdo[0x6041].bits[13]))
            
                node_1.switchOff()
            
                break
        
            if event in (None, "Homing 2"):
            
                node_2.switchOn()
            
                node_2.setHomingMode()
                node_2.homing()
                while(node_1.node.sdo[0x606c].raw != 0 and node_2.node.sdo[0x606c].raw != 0):
                    time.sleep(0.2)
                print("Homing finisched "+str(node_2.node.sdo[0x6041].bits[12]))
                print("Homing Fehler "+str(node_2.node.sdo[0x6041].bits[13]))
            
                node_2.switchOff()
            
                break
            
            if event in (None, "node_start"):
            
                node_1.switchOn()
                node_2.switchOn()
            
                setMoveHand()
            
                for i in range(0, cycle):
                    moveHand()
            
                node_1.switchOff()
                node_2.switchOff()
            
                window['act_posi_1'].update(node_1.getget_actual_position()*node_1.posi_factor)
                window['act_posi_2'].update(node_2.getget_actual_position()*node_2.posi_factor)
            
                break
        
            if event in (None, 'Update'):
                window['act_posi_1'].update(node_1.getget_actual_position()*node_1.posi_factor)
                window['act_posi_2'].update(node_2.getget_actual_position()*node_2.posi_factor)
                break
                
             #Wenn während der normalen Bewegungen die Fahrt gestopt wird oder ein Fehler aufgetreten ist wird die Schleife unterbrochen
            #If Motionbstopped while driving or an error has occurred, the loop is interrupted
            if ((X_Motor.requestStatus() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 22]
            or X_Motor.requestStatus() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 6])
            or (Y_Motor.requestStatus() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 22]
            or Y_Motor.requestStatus() == [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 8, 6])):

                break
            
            #Wenn ein Fehler aufgetreten ist wird die Schleife unterbrochen
            #If an error has occurred, the loop is interrupted
            X_Motor.checkError()
            Y_Motor.checkError()

            if X_Motor.error == 0 and Y_Motor.error == 0:
                error = 0
            else:
                error = 1
                break

            print ("Wait for Start")


#window['feedback'].Update(event)
window.close()








