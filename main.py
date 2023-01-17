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

""" ******************** GUI ******************** """

app = QApplication(sys.argv)

window = MainWindow(hand_1, hand_2, arm_x, arm_y)

sys.exit(app.exec_())
