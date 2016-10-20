"""
This version does not have a user program interfacing component...the rationale is that
you can simply import the file into your user program...though how a car program would run
in conjunction with a reactor loop is unclear

"""

from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.protocols.basic import IntNStringReceiver, LineOnlyReceiver
from twisted.internet import task, defer, endpoints
import sys, socket, struct

from twisted.internet import reactor

# hostName = 'YuchiLi-PC'
hostName = 'jeffrey-K501UX'

host = None
defaultTwistedServerPort = 8123
defaultUserPort = 5000

options = ['a', 'm', 'o', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# use win32 reactor if applicable
if sys.platform == 'win32':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()

# find hostname
def findHost():
    # TODO: error case for host not found
    addr = socket.gethostbyname(hostName)
    return addr

######################################################3

class SocketClientProtocol(LineOnlyReceiver):

    # after int prefix and other framing are removed:
    def lineReceived(self, line):
        self.factory.got_msg(line)

    def connectionMade(self):   # calls when connection is made with Twisted server
        print ("connected to twisted server")
        self.factory.clientReady(self)


class SocketClientFactory(ClientFactory):
    """ Created with callbacks for connection and receiving.
        send_msg can be used to send messages when connected.
    """
    protocol = SocketClientProtocol

    # def __init__(
    #         self,
    #         connect_success_callback,
    #         connect_fail_callback,
    #         recv_callback):

    def __init__(self):
        # self.connect_success_callback = connect_success_callback
        # self.connect_fail_callback = connect_fail_callback
        # self.recv_callback = recv_callback

        # store reference to client
        self.client = None

    def clientConnectionFailed(self, connector, reason):
        # self.connect_fail_callback(reason)
        print ("connection failed")
        reactor.stop()

    def clientReady(self, client):
        self.client = client
        # self.connect_success_callback()

    def got_msg(self, msg):
        # self.recv_callback()
        print (msg)

    def send_msg(self, msg):
        if self.client:
            self.client.sendLine(msg)

###########################################

if __name__ == '__main__':
    print('starting program')
    host = findHost()
    if(host is not None):
        print ('host is %s') %(host)
        reactor.connectTCP(host, defaultTwistedServerPort, SocketClientFactory())
        reactor.run()
    print ("could not find host")