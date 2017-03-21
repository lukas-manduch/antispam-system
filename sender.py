from mail_sender.sender import *
from email import *
import sys

if len(sys.argv) != 2:
    print("Script takes one argument - name of eml file")
    exit(1)
f = open(sys.argv[1], "r")
parser = Parser.FeedParser()
parser.feed(f.read())
msg = parser.close()

print(msg['Reply-to'])


#exit()
s = MailSender()
s.fake_mail(msg['Reply-to'], msg['From'] ,msg['Subject'], msg.get_payload())
