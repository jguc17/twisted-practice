import sys, optparse
from twisted.internet import defer, task, reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver  #for reading in user input
from twisted.internet import stdio


# TODO: REACTOR IS THE ONLY STATIC OBJECT WE CAN USE. WHEN USER INPUTS THE KEYWORD, USE CALLLATER TO CALL OTHER PROTOCOL'S METHOD

def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

  python get-poetry.py port

Of course, there need to be servers listening on those ports
for that to work.
"""

    parser = optparse.OptionParser(usage)

    _, addresses = parser.parse_args()

    if not addresses:
        print parser.format_help()
        parser.exit()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


class UserProtocol(LineReceiver):

    def __init__(self):
        self.sendingcallback = None #set in main

    def connectionMade(self):
        self.sendLine('User input console. Type \'help\' for help.')
        self.transport.write('>>> ')

    def dataReceived(self, data):

        self.sendLine('got input')

        # parse out actual input from the delimiter
        components = data.split()
        command = components[0].lower()

        if(command== 'feedme'):
            self.request()

        elif(command== 'quit'):
            self.sendLine('Peace out')
            self.transport.loseConnection()
            reactor.stop()  # stop reactor

        elif(command== 'help'):
            self.usage()

        self.transport.write('>>> ')

    def usage(self):
        self.sendLine('Input \'feed me\' to start receiving message from server\n '
                      'Input \'quit\' to exit the session\n')

    def request(self):
        if self.sendingcallback:
            self.sendingcallback("feedme")

class DataProtocol(Protocol):

    message = ""

    def connectionMade(self):
        print 'Laptop device: ', self, ' is connected.'

    def connectionLost(self, reason):
        self.messageReceived(self.message)

    # def messageReceived(self, message):
    #     self.factory.message_finished(message)

    def dataReceived(self, data):
        print 'DataProtocol.dataReceived called with\n: %s' % str(data)
        self.message += data

        #TODO: pass along to user program? through a callback?
        if self.factory.deferred is not None:
            d.callback(data)


class DataClientFactory(ClientFactory):

    protocol = DataProtocol # set protocol property

    def __init__(self):
        self.deferred = None
    #
    # def message_finished(self, message):
    #     if self.deferred is not None:
    #         d, self.deferred = self.deferred, None
    #         d.callback(message)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

    def sendRequest(self, message):
        self.transport.write(message)

        d = defer.deferred()
        d.addCallbacks(self.passToUser, self.serverFailed)

    def passToUser(self, data):
        #TODO: send position data to user program

    def serverFailed(self):
        #TODO: scenario when server fails to send expected response

if __name__ == '__main__':

    addresses = parse_args()
    stdio.StandardIO(UserProtocol())    # pass user protocol into stdio object

    messages = []
    errors = []

    def got_message(message):
        messages.append(message)
        print message

    def message_failed(err):
        print >> sys.stderr, 'Message failure:', err
        errors.append(err)

    host, port = addresses[0]

    d = defer.Deferred()
    d.addCallbacks(got_message, message_failed)

    data_factory = DataClientFactory()
    data_factory.deferred = d

    user_protocol = UserProtocol()
    user_protocol.sendingcallback = data_factory.sendRequest

    looper = task.LoopingCall(user_protocol.request)
    looper.start(1.5)

    reactor.connectTCP(host, port, data_factory)

    reactor.run()