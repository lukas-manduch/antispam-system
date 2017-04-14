
from mailer.personas import *
from mailer.imap import *
from mailer.eml_parser import *
from mailer.smtp import Smtp


from cleverwrap import CleverWrap
import nltk
import re
from email_reply_parser import *
from yandex_translate import YandexTranslate

import json
import random


def form_reply(from_, date, subject, message):
    return "\n\n---------- Original Message ----------\n" \
        "From: %s\nDate: %s\nSubject: %s\n\n%s" % (from_,
                                                 date,
                                                 subject,
                                                 message)

def name_from_address(from_):   # Argument is some email Reply-to
    name = re.sub('\W' , ' ', from_)
    name = from_.split()[0] + from_.split()[1]
    name = name.lower()
    return name
    

def create_folder_for_person(name):
    # Create folder for person
    if not os.path.exists("logs"):
        os.makedirs("logs")
    folder_path = os.path.join("logs" , name_from_address(name))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Copy questions to file
    if not os.path.exists("questions.json"): # File with general questions
        raise Exception("File with questions could not be found")
    if os.path.exists(os.path.join(folder_path, "questions.json")):
        # Already exists file with questions
        return folder_path
    fHandle = open("questions.json", "r")
    data = json.JSONDecoder().decode(fHandle.read())
    fHandle.close()
    random.seed()
    out_data = list()
    for list_ in data:
        out_data.append(list_[random.randint(0, len(list_) -1)])
    fHandle = open(os.path.join(folder_path, "questions.json"), "w")
    fHandle.write(json.JSONEncoder().encode(out_data))
    fHandle.close()
    return folder_path
    
def get_question(name):
    path = create_folder_for_person(name)
    fHandle = open(os.path.join(path, "questions.json"), "r" )
    questions = json.JSONDecoder().decode(fHandle.read())
    fHandle.close()
    if len(questions) == 0:
        return ""
    question = questions.pop()
    fHandle = open(os.path.join(path, "questions.json"),"w")
    fHandle.write(json.JSONEncoder().encode(questions))
    fHandle.close()
    return question
    
    
                

print(get_question("Neil Wilson <neilw243@yahoo.com>"))
        

# p = Personas(".\personas")

# cw = CleverWrap("CC1mmFptGklBB3wFbRtjhqGw7AA")
# print(cw.say("Hello"))
"""

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
            message = parse_reply(e.get_body().decode('utf-8',
                                                      errors='ignore'))
            if len(message) < 2:
                print("Too short message, skipping")
                continue
            reply_to_message = message # Will be used in email
            # Detect language
            # Classify
            # Pick chatbot
            if message.lower().find("address") != -1:
                reply = "Here are data you requested\n" \
                        "%s\n%s\n%s" % (pers['name'] + " " +
                                        pers['surname'],
                                        pers['address'],
                                        pers['email'])
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
            s.send()
"""
