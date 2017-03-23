from yahoo.email_parser import *
from yahoo.sender import *
from email import *
import sys

if len(sys.argv) != 2:
    print("Script takes one argument - name of eml file")
    print(str(len(sys.argv)) + " given")
    exit(1)

f = open(sys.argv[1], "r")
eml_parser = EmlParser(f.read())


s = MailSender()
s.fake_mail(eml_parser.get_from_address(),
            eml_parser.get_sender(),
            eml_parser.get_subject(),
            eml_parser.get_body())

