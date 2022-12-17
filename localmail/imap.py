# Copyright (C) 2012- Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
from twisted.internet import protocol
from twisted.mail import imap4
from twisted.mail._cred import LOGINCredentials, PLAINCredentials
from twisted.python.compat import nativeString
from zope.interface import implementer

from .inbox import INBOX


@implementer(imap4.IAccount)
class IMAPUserAccount(object):

    def listMailboxes(self, ref, wildcard):
        "only support one folder"
        return [("INBOX", INBOX)]

    def select(self, path, rw=True):
        "return the same mailbox for every path"
        return INBOX

    def create(self, path):
        "nothing to create"
        pass

    def delete(self, path):
        "delete the mailbox at path"
        raise imap4.MailboxException("Permission denied.")

    def rename(self, oldname, newname):
        "rename a mailbox"
        pass

    def isSubscribed(self, path):
        "return a true value if user is subscribed to the mailbox"
        return True

    def subscribe(self, path):
        return True

    def unsubscribe(self, path):
        return True


class IMAPServerProtocol(imap4.IMAP4Server):
    "Subclass of imap4.IMAP4Server that adds debugging."

    def lineReceived(self, line):
        imap4.IMAP4Server.lineReceived(self, line)

    def sendLine(self, line):
        imap4.IMAP4Server.sendLine(self, line)

    def do_ID(self, tag, args):
        args = args.upper().strip()
        print(args)
        self.sendLine(self, '* ID ("NAME" "Zimbra" "VERSION" "8.8.12_GA_3803" "RELEASE" "20190410012803")')
        self.sendLine(self, ' OK ID completed')

    def lookupCommand(self, cmd):
        print("_".join((self.state, nativeString(cmd.upper()))))
        return getattr(self, "_".join((self.state, nativeString(cmd.upper()))), None)


class TestServerIMAPFactory(protocol.Factory):
    protocol = IMAPServerProtocol
    portal = None  # placeholder
    noisy = False
    challengers = {
        b"LOGIN": LOGINCredentials,
        b"PLAIN": PLAINCredentials
    }

    def buildProtocol(self, address):
        p = self.protocol()
        # self.portal will be set up already "magically"
        p.portal = self.portal
        p.factory = self
        p.challengers = self.challengers
        return p
