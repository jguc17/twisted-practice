import sys, optparse
from urlparse import urlparse
from twisted.internet import defer, task, reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver  #for reading in user input
from twisted.internet import stdio


# TODO: REACTOR IS THE ONLY STATIC OBJECT WE CAN USE. WHEN USER INPUTS THE KEYWORD, USE CALLLATER TO CALL OTHER PROTOCOL'S METHOD

# those global flags are for the user to set
goAhead = False
endConnection = False


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

  python get-poetry.py port1 port2 port3 ...

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
    def connectionMade(self):
        self.sendLine('User input console. Type \'help\' for help.')
        self.transport.write('>>> ')

    def dataReceived(self, data):

        self.sendLine('got input')


        # parse out actual input from the delimiter
        components = data.split()
        # cutoff = 1
        # for i in range(len(components)):
        #
        #     self.sendLine('input %d: %s') %(i, components[i])
        #
        #     if (components[i] == '\n'):
        #         cutoff = i

        # command = ''.join(components[0:cutoff])

        command = components[0].lower()

        # self.sendLine(command)

        # how to pass this to small protocol?
        # procedure = self.handleInput(line)

        if(command== 'feedme'):
            # set global boolean flag
            global goAhead
            goAhead = True

        elif(command== 'quit'):
            self.sendLine('Peace out')
            self.transport.loseConnection()
            reactor.stop()  # stop reactor

        elif(command== 'help'):
            self.usage()

        self.transport.write('>>> ')



    # def handleInput(self, line):
    #     return {
    #         'feed me': 1,
    #         'help': 2,
    #         'quit': 3,
    #     }.get(line, 9)  # 9 is default if 'line' is not found

    def usage(self):
        self.sendLine('Input \'feed me\' to start receiving message from server\n '
                      'Input \'quit\' to exit the session\n')

class DataProtocol(Protocol):

    message = ""

    def connectionMade(self):
        print 'Laptop device: ', self, ' is connected.'

    def connectionLost(self, reason):
        self.messageReceived(self.message)

    def messageReceived(self, message):
        self.factory.message_finished(message)

    def dataReceived(self, data):
        # print 'DataProtocol.dataReceived called with\n: %s' % str(data)
        self.message += data

class DataClientFactory(ClientFactory):
    protocol = DataProtocol

    def __init__(self, deferred):
        self.deferred = deferred

    def message_finished(self, message):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(message)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

def get_message(host, port):
    """
    Download messsage from the given host and port. This function
    returns a Deferred which will be fired with the complete text of
    the poem or a Failure if the poem could not be downloaded.
    """
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = DataClientFactory(d)
    reactor.connectTCP(host, port, factory)
    return d


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

    # def message_done(message):
    #     # verify that we received either a msg or err from each address
    #     if len(messages) + len(errors) == len(addresses):
    #         reactor.stop()


    def check_flags():
        # print 'running check_flags'

        global endConnection
        global goAhead

        if (endConnection == True):
            endConnection = False
            reactor.stop()


        if (goAhead == True):
            print 'got the go ahead'
            goAhead = False
            # for addr in addresses:
            #     host, port = addr
            #     d = get_message(host, port)
            #     d.addCallbacks(got_message, message_failed)
                # d.addBoth(message_done)  # common end path for either a callback or errback


            # self.transport.write('feedme')


    for addr in addresses:
        host, port = addr
        d = get_message(host, port)
        d.addCallbacks(got_message, message_failed)

    looper = task.LoopingCall(check_flags)
    looper.start(2.0)

    # if(looper==True):
    #
    #     for addr in addresses:
    #         host, port = addr
    #         d = get_message(host, port)
    #         d.addCallbacks(got_message, message_failed)
    #         d.addBoth(message_done) # common end path for either a callback or errback

    reactor.run()

    for message in messages:
        print message