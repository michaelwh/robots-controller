import serial
import time

from multiprocessing import Process, Queue



class COMMANDS(object):
    MOVE_TOP_SERVO = 0x07
    MOVE_BOTTOM_SERVO = 0x08



def make_flags_byte(is_network=False, requires_ack=False, requires_global_ack=False, is_ack=False, is_global_ack=False):
    return (is_network) | (requires_ack << 1) | (requires_global_ack << 2) | (is_ack << 3) | (is_global_ack << 4)

def check_bit(byte, bitnum):
    return bool(byte & 1 << bitnum)

class Packet(object):
    def __init__(self, databytes):
        self.databytes = databytes

    def make_packet_bytearray(self):
        return bytearray((len(self.databytes),)) + self.databytes

    def is_network(self):
        return check_bit(self.databytes[0], 0)

    def requires_ack(self):
        return check_bit(self.databytes[0], 1)

    def requires_global_ack(self):
        return check_bit(self.databytes[0], 2)

    def is_ack(self):
        return check_bit(self.databytes[0], 3)

    def is_global_ack(self):
        return check_bit(self.databytes[0], 4)

    def __repr__(self):
        return self.databytes

#class ModuleConnection(object):
#    def __init__(self, serialport, baudrate=76800):
#        ser = serial.Serial(serialport, baudrate, timeout=1)

#    def send_packet(self, packet):
#        ser.write(packet.make_packet_bytearray())
    
#    def close(self):
#        ser.close()



class CommandUtil(object):
    packet_number = 0
    our_id = 255

    @classmethod
    def make_move_top_servo_packet(self, position, network_id_to=None):
        if network_id_to is None:
            return Packet(bytearray((make_flags_byte(), COMMANDS.MOVE_TOP_SERVO, position >> 8, 0xFF & position)))
        else:
            
            if CommandUtil.packet_number >= 255:
                CommandUtil.packet_number = 0
            else:
                CommandUtil.packet_number += 1
            return Packet(bytearray((make_flags_byte(), CommandUtil.packet_number, CommandUtil.our_id, network_id_to, COMMANDS.MOVE_TOP_SERVO, position >> 8, 0xFF & position)))

    @classmethod
    def make_move_bottom_servo_packet(self, position, network_id_to=None):
        if network_id_to is None:
            return Packet(bytearray((make_flags_byte(), COMMANDS.MOVE_BOTTOM_SERVO, position >> 8, 0xFF & position)))
        else:
            if CommandUtil.packet_number >= 255:
                CommandUtil.packet_number = 0
            else:
                CommandUtil.packet_number += 1
            return Packet(bytearray((make_flags_byte(), CommandUtil.packet_number, CommandUtil.our_id, network_id_to, COMMANDS.MOVE_BOTTOM_SERVO, position >> 8, 0xFF & position)))

class Module(object):
    def __init__(self, serialin, id_in):
        self.serial = serialin
        self.id = id_in


    def set_top_servo_position(self, position):
        packet = CommandUtil.make_move_top_servo_packet(position, self.id)
        print "Packet: ",
        for char in packet.make_packet_bytearray():
            print "%d" % char,
        print ""
        self.serial.write(packet.make_packet_bytearray())

    def set_bottom_servo_position(self, position):
        packet = CommandUtil.make_move_bottom_servo_packet(position, self.id)
        print "Packet: ",
        for char in packet.make_packet_bytearray():
            print "%d" % char,
        print ""
        self.serial.write(packet.make_packet_bytearray())
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Control modules via the command line")
    parser.add_argument('--serial-port', type=str, nargs='?', default='COM9', help="The name of the serial port to connect to.")
    args = parser.parse_args()

    ser = serial.Serial(args.serial_port, 76800, timeout=0.01)
        
    killflag = False
 
    modules = [Module(ser, 0)]
    
    position = 500
    positiondelta = 100
    while killflag == False:

        position += positiondelta
        if position > 1900:
            positiondelta = -positiondelta
        if position < 600:
            positiondelta = -positiondelta
        
        print position
        modules[0].set_top_servo_position(position)
        modules[0].set_bottom_servo_position(position)
        
        time.sleep(1)
        
    while False:
        bytein = ser.read(size=1)
        if bytein == 255:
            # this is a packet not a debug message
            lenbyte = ser.read(size=1)
            packet_data = ser.read(size=lenbyte)
            if len(packet_data) == lenbyte:
                # we have got a packet!
                packet = Packet(packet_data)

    
    ser.close()


    
