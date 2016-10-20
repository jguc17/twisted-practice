#!/usr/bin/python

#This implementation does not work with motive (yet)
#It just sends data over and over

import optparse, os, sys, socket
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineOnlyReceiver

defaultTwistedServerPort = 8123
# hostName = 'YuchiLi-PC'
hostName = 'jeffrey-K501UX'

# win32 support
if sys.platform == 'win32':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()

def parse_args():
    usage = """usage: %prog [options] file

This is the Twisted Server
Run it like this:

  python twisted_server2-0.py <path-to-poetry-file>
"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('--iface', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one poetry file.')

    file = args[0]

    if not os.path.exists(args[0]):
        parser.error('No such file: %s' % file)

    return options, file

class MyClientConnections(LineOnlyReceiver):

    # def __init__(self):
    def connectionMa1de(self):
        print "Got new client!"
        self.factory.clients.append(self)

        dfd = defer.Deferred()
        # dfd.addCallback(self.factory.parseText())
        dfd.addCallback(self.sendMsg)
        dfd.addCallback(self.factory.recycle(self))

        self.factory.deferList.append(dfd)

    def connectionLost(self, reason):
        print "Lost a client!"
        self.factory.clients.remove(self)

        #TODO: pass on reason

    def sendMsg(self, msg):
        self.sendLine(msg)

class MyServerFactory(Factory):
    protocol = MyClientConnections

    def __init__(self, text):
        self.clients = []
        self.text = text
        self.deferList = []

    def recycle(self, client):
        for index, c in enumerate(self.clients):
            if c == client:
                # self.deferList[index] = None
                dfd = defer.Deferred()
                dfd.addCallback(c.sendMsg(self.text))
                dfd.addCallback(self.recycle(c))
                self.deferList[index], dfd = dfd, None

    def sendToAll(self):
      for dfd in self.deferList:
        dfd.callback()

      # for c in self.clients:
      #   c.transport.write(message)


if __name__ == '__main__':
    options, file = parse_args()
    text = open(file).read()
    client_connection_factory = MyServerFactory(text)

    port = reactor.listenTCP(defaultTwistedServerPort, client_connection_factory, interface=socket.gethostbyname(hostName))
    l = task.LoopingCall(client_connection_factory.sendToAll())
    l.start(3.0)

    print 'Serving %s on %s.' % (file, port.getHost())

    reactor.run()