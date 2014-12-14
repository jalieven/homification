import imaplib
import email
import logging


class Gmail:
    def __init__(self, username=None, password=None, label=None):
        self.log = logging.getLogger('gmail')
        self.log.setLevel(logging.INFO)
        self.username = username
        self.password = password
        self.label = label

    def process_mailbox(self, M):
        rv, data = M.search(None, "ALL")
        messages = []
        if rv != 'OK':
            self.log.info("No messages found!")
            return
        for num in data[0].split():
            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                self.log.error("Failed getting message: " + num)
                return
            msg = email.message_from_string(data[0][1])
            subject = msg['Subject']
            timestamp = msg['Date']
            self.log.info('Received message:' + timestamp + ' - ' + subject)
            M.store(num, '+FLAGS', '\\Deleted')
            messages.append(subject)
        return messages

    def check(self):
        M = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            M.login(self.username, self.password)
            rv, mailboxes = M.list()
            if rv == 'OK':
                rv, data = M.select(self.label)
                if rv == 'OK':
                    return self.process_mailbox(M)
        except imaplib.IMAP4.error as e:
            self.log.error("GMail login failed! " + e.message)
        finally:
            M.expunge()
            M.close()
            M.logout()
