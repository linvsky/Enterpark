# coding=utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


class EmailAccountSettings(object):
    def __init__(self, account_settings):
        self.account_settings = account_settings

    @property
    def smtp_server(self):
        return self.account_settings['SMTP']

    @property
    def username(self):
        return self.account_settings['Username']

    @property
    def password(self):
        return self.account_settings['Password']

    @property
    def from_email(self):
        return self.account_settings['From']


class EmailSender(object):
    def __init__(self, smtp_server, username, password, default_sender, default_sender_email):
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.default_sender = default_sender
        self.default_sender_email = default_sender_email
        self.connected = False
        self.smtp_obj = None

    def connect(self):
        self.smtp_obj = smtplib.SMTP(timeout=30)
        self.smtp_obj.connect(self.smtp_server, 25)
        self.smtp_obj.login(self.username, self.password)
        self.connected = True

    def disconnect(self):
        if self.connected and self.smtp_obj:
            self.smtp_obj.close()
            self.smtp_obj = None

    def send(self, receivers, subject, message, sender=None, sender_email=None):
        if not self.connected:
            self.connect()

        if not self.connected:
            raise 'Failed to connect SMTP server %s' % self.smtp_server

        sender = sender and sender or self.default_sender
        sender_email = sender_email and sender_email or self.default_sender_email
        message = MIMEText(message, 'plain', 'utf-8')
        message['From'] = formataddr([sender, sender_email])
        message['To'] = ','.join(receivers)
        message['Subject'] = Header(subject, 'utf-8')

        self.smtp_obj = smtplib.SMTP()
        self.smtp_obj.connect(self.smtp_server, 25)
        self.smtp_obj.login(self.username, self.password)
        return self.smtp_obj.sendmail(sender_email, receivers, message.as_string())


if __name__ == '__main__':
    email_sender = EmailSender('<your smtp server>', '<your username>', '<your password>', '<any name>', '<any email>')
    email_sender.connect()
    email_sender.send(['victor880806@163.com'], 'Test Mail 1', 'This is a test mail.')
    email_sender.disconnect()
