from yahoo.sender import *
from mailer.eml_parser import EmlParser
from mailer.sender import *
import sys
import os

if len(sys.argv) != 3:
    print("Script takes two arguments "
          + str(len(sys.argv)) + " given" )
    print("1. Folder with eml files")
    print("2. Email address where to send messages")
    exit(1)

if not os.path.exists(sys.argv[1]):
    print("Path " + str(sys.argv[1]) + " doesn't exist")

files = os.listdir(sys.argv[1])

for file_name in files:
    fHandle = open(os.path.join(sys.argv[1],
                                file_name),
                   'br')
    parser = EmlParser(fHandle.read())
    fHandle.close()
    print(parser.get_context())
    mail = MailSender()
    mail.setprop('From', parser.get_sender())
    mail.setprop('Subject',parser.get_subject())
    mail.setprop('Reply-To', parser.get_from_address())
    mail.setprop('Date',parser.get_date())
    mail.setprop('To',sys.argv[2])
    body = parser.get_body()
    if len(body[0]) == 0: # length of plain
        mail.set_body(body[1], True)
    else:
        mail.set_body(body[0])
    mail.send_mail(sys.argv[2])


'''

s = MailSender()
s.fake_mail(eml_parser.get_from_address(),
            eml_parser.get_sender(),
            eml_parser.get_subject(),
            eml_parser.get_body())

'''
