# This is the Twisted Fast Poetry Server, version 1.0

import optparse, os

from twisted.internet.protocol import ServerFactory, Protocol
from twisted.protocols.basic import LineReceiver


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


class SmallProtocol(LineReceiver):

    def connectionMade(self):
        self.transport.write(self.factory.text)
        self.factory.clients.append(self)
        # self.transport.loseConnection()


    def dataReceived(self, data):

        components = data.split()

        command = components[0].lower()

        print 'received %s' % command

        if(command=='feedme'):
            self.factory.giveMessage(self)

    # def sendMsg(self, text):
    #     self.sendLine(text)


class SmallFactory(ServerFactory):

    protocol = SmallProtocol

    def __init__(self, text):
        self.text = text
        self.clients = []

    def giveMessage(self, client):
        client.transport.write(self.text)

def main():
    options, file = parse_args()

    text = open(file).read()

    factory = SmallFactory(text)

    from twisted.internet import reactor


    # port = reactor.listenTCP(8123, factory, interface='172.27.102.58')
    port = reactor.listenTCP(8123, factory, interface='127.0.1.1')

    print 'Serving %s on %s.' % (file, port.getHost())

    reactor.run()


if __name__ == '__main__':
    main()
