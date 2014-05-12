#!/usr/bin/env python

import serial, time
import sys
import argparse

class Multimeter(object):
    def __init__(self,port='/dev/ttyUSB0'):
        ser = serial.Serial()
        ser.port = port
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
        self.id = None

    def connect(self):
        self.ser.open()

    def writeCommand(self,cmd):
        wcmd = cmd + '\n'
        self.ser.write(wcmd)
        time.sleep(0.05)

    def getId(self):
        self.writeCommand('*IDN?')
        resp = self.ser.readline()
        self.id = resp
        return resp

    def reset(self):
        self.writeCommand('*RST')
        time.sleep(1)

    def clear(self):
        self.writeCommand('*CLS')

    def setSystem(self,cmd):
        wcmd = 'SYST:'+cmd
        self.writeCommand(wcmd)

    def getSystem(self):
        self.writeCommand('SYST?')
        resp = self.ser.readline()
        print resp

    def display(self,state):
        if state:
            self.writeCommand('DISPLAY 1')
        else:
            self.writeCommand('DISPLAY 0')


    def setupForRemote(self, reset=True):
        self.connect()
        self.getId()
        self.clear()

        if reset:
            self.reset()
            self.clear()

        self.display(True)
        self.setSystem('REM')


    def measure(self,what="VOLT:DC",range=10.0,resolution=0.003):
        wcmd = 'MEAS:'+what+"? %f,%f"%(range,resolution,)
        wcmd = 'MEAS:'+what+"? %f"%(range)
        self.writeCommand(wcmd)
        return self.readResult()

    def start(self,what="VOLT:DC",range=10.0,resolution=0.003,samples=1):
        wcmd = 'CONF:'+what+" %f"%(range)
        self.writeCommand(wcmd)
        self.writeCommand("SAMPLe:COUNt %f" % (samples))
        self.writeCommand("TRIG:SOUR IMM")
        #self.writeCommand("INIT")
        #self.writeCommand("FETC?")

    def read(self):
        self.writeCommand("READ?")
        return self.readResult()

    def readResult(self):
        resp = self.ser.readline()
        if not resp:
            self.readError()
            return -1
        return float(resp)

    def readError(self):
        self.writeCommand('SYST:ERROR?')
        resp = self.ser.readline()
        print resp
        return resp

    def doCommand(self,what):
        self.writeCommand(what)
        resp = self.ser.readline()
        if resp:
            print resp
        return resp

if __name__ == "__main__":
    csv = None
    devices = {}

    parser = argparse.ArgumentParser(description='SCPI Interface')
    parser.add_argument('-p','--ports',
        dest="ports",
        action='append',
        default=[],
        help="Ports to read from, can read on multiple ports simultaneously.")
    parser.add_argument("-o","--output",
        dest="output",
        default=None,
        help="CSV output")

    args = parser.parse_args()
    ports = args.ports

    if len(ports) == 0:
        ports = ["/dev/ttyUSB0"]

    if args.output:
        csv = open(args.output,"w+")
        csv.write("Nb,Time (s)")
        for i in range(1, len(ports)):
            csv.write(",Value %d (mA)" % (i))
        csv.write("\n")

    for port in ports:
        device = Multimeter(port)
        device.setupForRemote(True) #False)
        device.doCommand("SYSTem:BEEPer:STATe OFF")
        device.doCommand("TRIGger:DELay:AUTO ON")

        devices[port] = device

    i = 1
    tsStart = time.time()

    for port in ports:
        devices[port].start("CURR:DC", range=0.5, samples=1)

    try:
        while 1:
            #amp = a.measure("CURR:DC", 0.1)
            #amp = a.ser.readline()
            readings = {}
            for port in ports:
                readings[port] = devices[port].read()

            tsNow = time.time()
            tsOffset = tsNow - tsStart

            sys.stdout.write("%d:" % (tsOffset))
            for port in ports:
                sys.stdout.write(" %f" % readings[port])
            sys.stdout.write("\n")

            if csv:
                line = "%d,%f\n" % (i, tsOffset)
                for port in ports:
                    line += ",%f" % (readings[port] * 1000)
                line += "\n"

                #line = line.replace(".",",")
                csv.write(line)
                csv.flush()

            i += 1

    except (KeyboardInterrupt, SystemExit):
        csv.close()
        exit(0)
