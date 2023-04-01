import canopen
from controller.ArmController import D1
from controller.HandController import Drive
from widget.GUI import *

os.system("sudo ifconfig can0 down")
os.system("sudo /sbin/ip link set can0 up type can bitrate 125000")
os.system("sudo ifconfig can0 up")

network = canopen.Network()
network.connect(channel='can0', bustype='socketcan', bitrate=125000)

hand_1 = Drive(127, network)
hand_2 = Drive(126, network)

arm_x = D1("169.254.0.1", 502, "X-Axis")
arm_y = D1("169.254.0.2", 502, "Y-Axis")

arm_x.homing(60, 300)
arm_y.homing(60, 300)

hand_1.move_to_target_position(10)
hand_2.move_to_target_position(10)

# profile_position_mode(velo, acc, pos):
arm_x.profile_position_mode(100, 100, 100)
arm_y.profile_position_mode(100, 100, 100)