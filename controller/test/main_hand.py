import sys
sys.path.append("..")

import canopen
from widget.HandWidget import *
from controller.HandController import Drive

os.system("sudo ifconfig can0 down")
os.system("sudo /sbin/ip link set can0 up type can bitrate 125000")
os.system("sudo ifconfig can0 up")

network = canopen.Network()
network.connect(channel='can0', bustype='socketcan', bitrate=125000)

node_1 = Drive(127, network)
node_2 = Drive(126, network)

""" ******************** GUI (only for unit test) ******************** """

app = QApplication(sys.argv)

window = HandUser(node_1, node_2)

sys.exit(app.exec_())
