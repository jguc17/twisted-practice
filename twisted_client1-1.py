import sys, optparse
from urlparse import urlparse
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.serialport import SerialPort

# serServ = None

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

class SmallProtocol(Protocol):

    message = ""

    def connectionMade(self):
        global serServ
        serServ = self
        print 'Laptop device: ', serServ, ' is connected.'

    def connectionLost(self, reason):
        self.messageReceived(self.message)

    def messageReceived(self, message):
        self.factory.message_finished(message)

    # def cmdReceived(self, cmd):
    #     serServ.transport.write(cmd)
    #     print cmd, ' - sent to laptop.'
    #     pass

    def dataReceived(self, data):
        print 'SmallProtocol.dataReceived called with: %s', str(data)
        self.message += data

class SmallClientFactory(ClientFactory):
    protocol = SmallProtocol

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
    Download a poem from the given host and port. This function
    returns a Deferred which will be fired with the complete text of
    the poem or a Failure if the poem could not be downloaded.
    """
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = SmallClientFactory(d)
    reactor.connectTCP(host, port, factory)
    return d

# class HTTPserver(resource.Resource):
#     isLeaf = True
#     def render_GET(self, request):      #passes the data from the get request
#         print 'HTTP request received'
#         myPC = USBclient()
#         stringit = str(request)
#         parse = stringit.split()
#         command, path, version = parse
#         myArduino.cmdReceived(path)

# class cmdTransport(Protocol):
#     def __init__(self, factory):
#         self.factory = factory
#
# class cmdTransportFactory(Factory):
#     protocol = cmdTransport

if __name__ == '__main__':
    # HTTPsetup = server.Site(HTTPserver())
    # reactor.listenTCP(5000, HTTPsetup)
    SerialPort(USBclient(), '/dev/ttyACM0', reactor, baudrate='115200')

    #######
    addresses = parse_args()

    from twisted.internet import reactor

    messages = []
    errors = []

    def got_message(message):
        messages.append(message)

    def message_failed(err):
        print >> sys.stderr, 'Message failure:', err
        errors.append(err)

    def message_done():
        # verify that we received either a msg or err from each address
        if len(messages) + len(errors) == len(addresses):
            reactor.stop()

    for addr in addresses:
        host, port = addr
        d = get_message(host, port)
        d.addCallbacks(got_message, message_failed)
        d.addBoth(message_done)

    reactor.run()

    for message in messages:
        print message