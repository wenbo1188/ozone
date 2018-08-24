import smtplib
import threading
from email.mime.text import MIMEText
from email.header import Header

class EmailReminder:
    '''
    Reminder by sending email
    '''

    def __init__(self, mail_server, mail_port, mail_username, mail_password, debug_mode = False, logger = None):
        try:
            self.smtpserver = smtplib.SMTP_SSL(mail_server, mail_port)
        except smtplib.SMTPConnectError as err:
            self.smtpserver = None
            if logger != None:
                logger.error("{}".format(err))
        self.mail_server = mail_server
        self.mail_port = mail_port
        self.mail_username = mail_username
        self.mail_password = mail_password
        self.debug_mode = debug_mode
        self.logger = logger

        # set debug level
        if (debug_mode == True):
            self.smtpserver.set_debuglevel(1)

    def send(self, receiver, receiver_name, message_content):
        self.logger.info("Start to send email")
        message = MIMEText(message_content, 'text', 'utf-8')
        message['Subject'] = Header("Ozone消息提醒", 'utf-8')
        message['From'] = 'Ozone消息管家<{sender_addr}>'.format(sender_addr = self.mail_username)
        message['To'] = '{receiver_name}<{receiver_addr}>'.format(receiver_name = receiver_name, receiver_addr = receiver)

        mail_thread = threading.Thread(target = self.send_async_email, args = [message, receiver])
        mail_thread.start()

    def send_async_email(self, msg, receiver):
        '''
        Server login
        '''

        try:
            self.smtpserver.login(self.mail_username, self.mail_password)
            self.smtpserver.sendmail(self.mail_username, [receiver], msg.as_string())
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPSenderRefused) as err:
            self.logger.error("Fail to send email:\n{}".format(err))
        finally:
            if self.smtpserver != None:
                self.smtpserver.quit() 
