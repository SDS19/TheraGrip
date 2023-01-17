import time

from canopen.profiles.p402 import BaseNode402


class Drive:
    def __init__(self, node_id, network):
        self.node_id = node_id
        
        self.network = network

        self.node = BaseNode402(node_id, 'controller/obj dict/mclm.eds')

        network.add_node(self.node)

        self.node.nmt.state = 'OPERATIONAL'
        # self.pdo_config()

        """ ********** variable ********** """

        self.start_position = 0

        self.end_position = 0

        self.range = 0

        self.cycle = 3

        self.position_factor = self.get_position_factor()

        self.velocity = 0x32  # target velocity: 0x32 = 50

    """ ********** Step 1: P74 CiA 402 CANopen Device Profile **********

    This device profile has a >>control state machine<< for controlling the behavior of the drive.

    0x6040: Controlword
    0x6041: Statusword

    Switch On Disabled 
    - Shutdown => Ready to Switch On  (0x0006)
    - Switch On => Switched On (0x0007)
    - Enable Operation => Operation Enabled (0x000F)
    - Disable Operation => Switched On
    """

    def operation_enabled(self):
        self.shut_down()
        self.switch_on()
        self.enable_operation()

    def shut_down(self):
        self.node.sdo[0x6040].raw = 0x06

    def switch_on(self):
        self.node.sdo[0x6040].raw = 0x07

    def enable_operation(self):
        self.node.sdo[0x6040].raw = 0x0F

    def halt(self):
        self.node.sdo[0x6040].bits[8] = 1  # stop drive

    """ ******************** Step 2: P127 Modes of Operation ******************** 

    Profile Position Mode: 1
    Profile Velocity Mode: 3
    Homing Mode:           6

        ********** P87 Homing Mode ********** """

    # 0x6060: Modes of Operation
    # 0x6098: Homing Method
    # 0x6040: Controlword -> 4: New set-point/Homing operation start
    def homing_to_actual_position(self):
        self.operation_enabled()  # power on
        self.node.sdo[0x6060].raw = 0x06  # 0x06: Homing Mode
        self.node.sdo[0x6098].raw = 0x23  # 0x23 = 35: Homing at actual position
        self.node.sdo[0x6040].bits[4] = 1  # start to move
        if self.node_id == 127:
            print("node 1: ")
        else:
            print("node 2: ")
        print("Homing Attained (1) = " + str(self.node.sdo[0x6041].bits[12]) +
              ", Homing Error (0) = " + str(self.node.sdo[0x6041].bits[13]))

    """ ********** Profile Position Mode ********** """

    # 0x607E: Polarity (P129)
    # Bit 7 = 1 negative Bewegungsrichtung im Positionierbetrieb
    # Bit 6 = 1 negative Bewegungsrichtung im Geschwindigkeitsbetrieb
    def set_negative_move_direction(self):
        self.node.sdo[0x607E].bits[7] = 1

    # 0x6060: Modes of Operation -> 0x01: Profile Position Mode
    # 0x6061: Modes of Operation Display
    # 0x6067: Position Window
    def set_profile_position_mode(self):
        self.position_limits_off()
        self.node.sdo[0x6060].raw = 0x01
        self.node.sdo[0x6067].raw = 0x3E8  # 0x3E8 = 1000

    # 0x2338: General Settings -> 3: Active Position Limits in Position Mode
    def position_limits_off(self):
        self.node.sdo[0x2338][3].raw = 0

    # 0x607A: Target Position
    # 0x6040: Controlword -> 4: New set-point/Homing operation start
    def move_to_target_position(self, target_position):
        self.operation_enabled()
        self.node.sdo[0x607A].raw = target_position
        self.node.sdo[0x6040].bits[4] = 1  # start to move

    # P80 => Position Factor
    # 0x6063: Position Actual Internal Value (in internen Einheiten)
    # 0x6064: Position Actual Value (in benutzerdefinierten Einheiten)
    def get_actual_position(self):
        position = self.node.sdo[0x6064].raw
        return position

    # 0x6093: Position Factor
    def get_position_factor(self):
        numerator = int.from_bytes(self.node.sdo.upload(0x6093, 1)[0:2], byteorder='little')
        divisior = int.from_bytes(self.node.sdo.upload(0x6093, 2)[0:2], byteorder='little')
        return (numerator / divisior) / 100

    """ ********** SDO: get data ********** """

    # 0x6081: Profile Velocity
    def set_target_velocity(self, target_velocity):
        self.node.sdo['Profile Velocity'].raw = target_velocity

    # 0x606C: Velocity Actual Value
    def get_actual_velocity(self):
        velocity = self.node.sdo[0x606C].raw
        # print("Velocity Actual Value: " + str(velocity))
        return velocity
    
    # 0x6078: Current Actual Value
    def get_actual_current(self):
        current = self.node.sdo[0x6078].raw
        # print("Current Actual Value: " + str(current))
        return current

    """ ********** PDO: get data  
    
    https://github.com/christiansandberg/canopen
    
    ********** """

    def pdo_config(self):        
        # Read PDO configuration from node
        self.node.tpdo.read()
        self.node.rpdo.read()
        
        self.node.nmt.state = 'PRE-OPERATIONAL'

        # Re-map TPDO[1]
        self.node.tpdo[1].clear()
        # self.node.tpdo[1].add_variable('6064')
        self.node.tpdo[1].add_variable('Position Actual Value')
        self.node.tpdo[1].trans_type = 254
        # self.node.tpdo[1].event_timer = 10
        self.node.tpdo[1].enabled = True
        # self.node.tpdo[1].save()  # Save new PDO configuration to node
        
        # self.node.tpdo[2].clear()
        # self.node.tpdo[2].add_variable('Velocity Actual Value')
        # self.node.tpdo[2].trans_type = 254
        # self.node.tpdo[2].enabled = True
        # self.node.tpdo[2].save()
        
        # self.node.tpdo[3].clear()
        # self.node.tpdo[3].add_variable('Current Actual Value')
        # self.node.tpdo[3].trans_type = 254
        # self.node.tpdo[3].enabled = True
        
        self.node.tpdo.save()  

        self.network.sync.start(0.1)  # Transmit SYNC every 100 ms

        # Change state to operational (NMT start)
        self.node.nmt.state = 'OPERATIONAL'
        
        self.node.tpdo[1].wait_for_reception()
        position = self.node.tpdo[1]['Position Actual Value'].phys

    def rpdo(self):
        # Read a value from TPDO[1]
        self.node.tpdo[1].wait_for_reception()
        position = self.node.tpdo[1]['Position Actual Value'].phys
        # velocity = self.node.tpdo[2]['Velocity Actual Value'].phys
        # current = self.node.tpdo[3]['Current Actual Value'].raw
        return [current, position, velocity]
