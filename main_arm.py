from widget.ArmWidget import *
from controller.ArmController import D1


x_axis = D1("169.254.0.1", 502, "X-Axis")
y_axis = D1("169.254.0.2", 502, "Y-Axis")

x_axis.homing(60, 300)
y_axis.homing(60, 300)

""" ******************** GUI (only for unit test) ******************** """

app = QApplication(sys.argv)

window = ArmDev(x_axis, y_axis)

sys.exit(app.exec_())