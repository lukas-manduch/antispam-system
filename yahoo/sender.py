import smtplib
from email.mime.text import MIMEText

class MailSender:
    def __init__(self):
        self.server = smtplib.SMTP("localhost")
        self.server.ehlo()
        self.server.set_debuglevel(1)


    def fake_mail(self, from_address, from_name, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_name
        msg['To'] = 'neilw243@yahoo.com'
        self.server.sendmail(
            from_address, 'neilw243@yahoo.com', msg.as_string())
        
    def __del__(self):
        self.server.quit()
