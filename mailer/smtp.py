import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



class Smtp:
    def __init__(self, host, login, password):
        self.connection = smtplib.SMTP_SSL(host)
        self.connection.ehlo()
        # self.connection.set_debuglevel(1)
        self.connection.login(login, password)
        self.message = MIMEMultipart()

    def __del__(self):
        # self.connection.quit()
        pass

    
    def set(self, name, content):
        self.message[name] = content

    def set_body(self, content):
        self.message.attach(MIMEText(content, 'plain'))

    def send(self):
        self.connection.sendmail(self.message['From'],
                                 self.message['To'],
                                 self.message.as_string())
        return self.message.as_string()
