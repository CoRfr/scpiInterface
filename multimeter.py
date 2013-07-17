import serial


class Multimeter(object):
    def __init__(self,port='/dev/ttyUSB0'):
        ser = serial.Serial()
        ser.port = '/dev/ttyUSB0'
        ser.baudrate = 9600
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout = 1
        ser.xonxoff = False
        ser.rtscts = False
        ser.dsrdtr = False
        ser.writeTimeout = 2
        self.ser = ser

    def connect(self):
        self.ser.open()

    def writeCommand(self,cmd):
        wcmd = cmd + '\n'
        self.ser.write(wcmd)

    def getId(self):
        self.writeCommand('*IDN?')
        resp = self.ser.readline()
        return resp


if __name__ == "__main__":
    a = Multimeter()
    a.connect()
    id = a.getId()
    print id

