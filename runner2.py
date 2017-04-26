
from mailer.personas import *
from mailer.imap import *
from mailer.eml_parser import *
from mailer.smtp import Smtp
from mailer.helpers import *

from email_reply_parser import *

import re
import random

QUESTIONS = "questions.json"
LOGS = "logs"

p = Personas("personas")

while p.next():
    pers = p.get_data()
    print( "Acting as " + p.get_data()["email"])
    i = Imap(pers["imap-server"],
             pers["imap-login"],
             pers["imap-password"])
    while i.next():
        while i.next_message():
            print("Found message with subject")
            e = EmlParser(i.get_message())
            body = e.get_body()
            print(e.get_subject())
            message = parse_reply(e.get_context().decode('utf-8',
                                                      errors='ignore'))
            if len(message) < 2:
                print("Too short message, skipping")
                continue
            # Will be used in email
            reply_to_message = body[0].decode('utf-8',
                                              errors='ignore')
            print("message")
            print(message)
            message = to_english(message)
            print('-----------')            
            # Classify
            if e.get_subject().lower().find("re:") == -1:
                # Use classifier
                pass
            reply = get_question(e.get_from_address(),pers['email'])
            if len(reply) == 0:
                reply = cleverbot_reply(message)
            print("Got reply")
            print(reply)
            # Personalize
            reply = reply + "\n\n%s\n" % (pers['name'])
            # Send response
            s = Smtp(pers['smtp-server'],
                     pers['smtp-login'],
                     pers['smtp-password'])
            s.set('From', pers['email'])
            s.set('To', e.get_from_address())
            s.set('Subject', "Re: "+e.get_subject())
            s.set_body(reply + form_reply(
                e.get_sender(),
                e.get_date(),
                e.get_subject(),
                reply_to_message))
            sent_m = s.send()
            # Save message to file
            fHandle = open(find_free_file(
                create_folder_for_person(e.get_sender(),
                                         pers['email'])),
                           "w")
            fHandle.write(reply)
            fHandle.close()
            i.add_sent(sent_m)
