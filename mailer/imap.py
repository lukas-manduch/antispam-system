import imaplib
import re
import quopri
import datetime


"""
Imap class, usage:

i = Imap(host, name, password)
while i.next(): # -> For each mailbox
    while i.next_message():
        i.get_message()
"""


def get_mailbox(line):
    line = (line).decode('utf-8', errors='ignore')
    pattern = re.compile(r'.*"(?P<mailbox>[\w\s]{1,})"')
    mailbox_name = pattern.match(line).group('mailbox')
    return mailbox_name


class Imap:
    def __init__(self, host, name, password):
        self.connection = imaplib.IMAP4_SSL(host)
        self.connection.login(name, password)
        self.mailboxes = list() # list of names of mailboxes
        self.ids = list() # list of ids of messages in current mailbox
        self.content = str() # eml formatted message
        self.open = False    # Should conection be closed?
        typ, data = self.connection.list()
        for line in data:
            m_name = get_mailbox(line)
            self.mailboxes.append(m_name)

    def __del__(self):
        try:
            if self.open:
                self.connection.close()
            self.connection.logout()
        except Exception as e:
            print("Error while closing imap, " + str(e))
    
    def next(self) -> bool:
        """
        Find next mailbox with some unread messages or return false
        Throw away current data
        """
        if len(self.mailboxes) == 0:
            return False
        if self.open:
            self.connection.close()
            self.open = False
        m_name = self.mailboxes.pop()
        try:
            if self.connection.select(m_name)[0] != 'OK':
                raise Exception
            self.open = True
        except Exception as e:
            print("Mailbox " + m_name + " error:")
            print(e)
            return self.next()
        # Everything went well and we are in mailbox

        typ, ids = self.connection.search(None, 'UNSEEN')
        if typ != 'OK':
            print("Error while searching mailbox" + m_name)
            return self.next()
        self.ids = ids[0].split()
        return True


    def next_message(self) -> bool:
        if len(self.ids) == 0:
            return False
        eid = self.ids.pop()
        typ, data = self.connection.fetch(eid, '(RFC822)')
        # self.content = quopri.decodestring(data[0][1]).decode('utf-8',
                                                              # 'ignore')
        self.connection.store(eid, '+FLAGS', '\Seen')
        self.content = data[0][1]
        if type(self.content) != bytes: # Heuristic
            self.content = data[1][1]
        return True

    def get_message(self) -> str:
        return self.content


    def add_sent(self, message) -> bool:
        try:
            self.connection.append('Sent',
                                   '\Seen',
                                   datetime.datetime.now(datetime.timezone.utc),
                                   message.encode('utf-8',errors='ignore'))
        except Exception as e:
            print("ERROR: message not saved in Sent: " + str(e))


