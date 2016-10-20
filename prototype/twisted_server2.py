#This implementation is more aligned with the one written by Stephen.
#It features an input protocol that should read in information from the C++ streaming app


#!/usr/bin/env python

from twisted.python import log, usage
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols import basic
from struct import *
import sys

# win32 support
if sys.platform == 'win32':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()


class OutputProtocol(basic.LineOnlyReceiver):

class MotiveProtocol(basic.LineOnlyReceiver):

class MotiveFactory(Factory):



if __name__ == '__main__':
    from twisted.internet.import reactor
    from twisted.internet.serialport import SerialPort #do we need serial port?

