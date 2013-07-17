This is a very simple, thin python wrapper to talk to SCPI devices like multimeters, etc. To test, just say python multimeter.py on a terminal. It assumes the serial port to use is '/dev/ttyUSB0' by default and depends on the pyserial library.

There's a lot to be done. Right now, it just supports the following.
-Reset (RST)
-Identification Number (IDN)
-System:Remote/Local
-MEASure

This is an excellent guide on SCPI for those who want to build/read/add more.
http://www.phas.ubc.ca/~phys409/HPManuals/HP34401A_RemoteGuide.pdf

Error handling is completlely absent, the only reason I even wrote this and uploaded this is because I couldn't find something existing that would let me just take a couple of measurements off the multimeter.
