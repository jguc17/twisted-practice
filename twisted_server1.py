# This is the Twisted Fast Poetry Server, version 1.0

import optparse, os

from twisted.internet.protocol import ServerFactory, Protocol


def parse_args():
    usage = """usage: %prog [options] file

This is the Twisted Server
Run it like this:

  python fastpoetry.py <path-to-poetry-file>

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


class SmallProtocol(Protocol):

    def connectionMade(self):
        self.transport.write(self.factory.text)
        self.transport.loseConnection()

class SmallFactory(ServerFactory):

    protocol = SmallProtocol

    def __init__(self, text):
        self.text = text

def main():
    options, file = parse_args()

    text = open(file).read()

    factory = SmallFactory(text)

    from twisted.internet import reactor

    # port = reactor.listenTCP(options.port or 0, factory,
    #                          interface=options.iface)


    # print "options interface is " + options.iface




    # port = reactor.listenTCP(8123, factory, "DESKTOP-C69NTL2")
    # port = reactor.listenTCP(8123, factory, "localhost")
    port = reactor.listenTCP(8123, factory, interface='172.27.102.129')
    # port = reactor.listenTCP(8123, factory, "172.27.102.132")

    print 'Serving %s on %s.' % (file, port.getHost())

    reactor.run()


if __name__ == '__main__':
    main()
