from twisted.cred import portal, checkers, credentials
from twisted.conch import error, avatar, recvline, interfaces as conchinterfaces
from twisted.conch.ssh import factory, userauth, connection, keys, session, common
from twisted.conch.insults import insults
from twisted.conch import checkers
from twisted.internet import reactor
from zope.interface import implements
from Crypto.PublicKey import RSA
import os
import dbauth

## SHELL implementation
# Subclass of HistoricRecvLine to build command-line shells
class SSHProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("Welcome to the martinord SSH server")
        self.terminal.nextLine()
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write("> ")

    def showError(self, e):
        self.terminal.write("Error: %s" % e)
        self.terminal.nextLine()

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None) # gets the command

    # Behaviour of the shell
    def lineReceived(self, line):
        line = line.strip()
        if line:
            cmdline = line.split()
            cmd = cmdline[0]   # gets the command
            args = cmdline[1:] # gets the arguments of the command
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception, e:
                    self.showError(e)
            else:
                self.terminal.write("%s is not a command" % cmd)
                self.terminal.nextLine()
        self.showPrompt()

    # COMMANDS
    def do_echo(self, *args):
        # Echo a string. Usage: echo line of text
        self.terminal.write(" ".join(args))
        self.terminal.nextLine()

    def do_clear(self):
        # Clears the screen. Usage: clean
        self.terminal.reset()

    def do_quit(self):
        # Ends the session. Usage: quit
        self.terminal.write("See you soon")
        self.terminal.nextLine()
        self.terminal.loseConnection()


## Avatar (user class)
# Subclass of Twisted ConchUser
# Implements the ISession Conch Interface
class SSHAvatar(avatar.ConchUser):
    implements(conchinterfaces.ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session' : session.SSHSession})

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SSHProtocol, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def closed(self):
        pass

## Realm
# Implements the IRealm
class SSHRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarID, mind, *interfaces):
        if conchinterfaces.IConchUser in interfaces:
            return interfaces[0], SSHAvatar(avatarID), lambda: None
        else:
            raise Exception, "No supported interfaces found."

# Generates the RSA KEYS of the server
def getRSAKeys():
    if not (os.path.exists('public.key') and os.path.exists('private.key')):
        # GENERATE RSA key pair
        print "Generating RSA keypair ..."
        KEY_LENGTH = 1024
        rsak = RSA.generate(KEY_LENGTH)
        publicKeyString = rsak.exportKey(pkcs=1)
        privateKeyString = rsak.exportKey(pkcs=8)
        # save to files
        file('public.key', 'w+b').write(publicKeyString)
        file('private.key', 'w+b').write(privateKeyString)
        print "OK"
    else:
        publicKeyString = file('public.key').read()
        privateKeyString = file('private.key').read()

    return publicKeyString, privateKeyString

# MAIN
if __name__ == "__main__":
    sshFactory = factory.SSHFactory()
    sshFactory.portal = portal.Portal(
        SSHRealm()
    )

    sshFactory.portal.registerChecker(
        checkers.UNIXPasswordDatabase()
    )

    # Set SSH key pair
    pubKeyStr, privKeyStr = getRSAKeys()
    sshFactory.publicKeys = {
        'ssh-rsa': keys.Key.fromString(pubKeyStr)
    }
    sshFactory.privateKeys = {
        'ssh-rsa' : keys.Key.fromString(pubKeyStr)
    }

    # Init
    reactor.listenTCP(2222, sshFactory)
    reactor.run()
