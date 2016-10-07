#!/usr/bin/python

from twisted.internet import task
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ServerFactory

class PollingIOThingy(object):
    def __init__(self):
        self.sendingcallback = None # Note I'm pushing sendToAll into here in main
        self.iotries = 0

    def pollingtry(self):
        self.iotries += 1
        print "Polling runs: " + str(self.iotries)
        if self.sendingcallback:
            self.sendingcallback("Polling runs: " + str(self.iotries) + "\n")

class MyClientConnections(Protocol):
    def connectionMade(self):
        print "Got new client!"
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print "Lost a client!"
        self.factory.clients.remove(self)

class MyServerFactory(ServerFactory):
    protocol = MyClientConnections

    def __init__(self):
        self.clients = []

    def sendToAll(self, message):
      for c in self.clients:
        c.transport.write(message)

def main():
    client_connection_factory = MyServerFactory()

    polling_stuff = PollingIOThingy()

    # the following line is what this example is all about:
    polling_stuff.sendingcallback = client_connection_factory.sendToAll
    # push the client connections send def into my polling class

    # if you want to run something every second (instead of 1 second after
    # the end of your last code run, which could vary) do:
    l = task.LoopingCall(polling_stuff.pollingtry)
    l.start(1.0)
    # from: https://twistedmatrix.com/documents/12.3.0/core/howto/time.html

    reactor.listenTCP(5000, client_connection_factory)
    reactor.run()

if __name__ == '__main__':
  main()