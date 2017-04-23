
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

QUESTIONS = "questions.json"
LOGS = "logs"

def form_reply(from_, date, subject, message):
    return "\n\n---------- Original Message ----------\n" \
        "From: %s\nDate: %s\nSubject: %s\n\n%s" % (from_,
                                                 date,
                                                 subject,
                                                 message)

def name_from_address(from_):   # Argument is some email Reply-to
    name = re.search('(?P<mail>[\w.-]+@[\w.-]+.\w+)',
                     from_).group('mail')
    name = re.sub('\W' , '_', name)
    #name = from_.split()[0] + from_.split()[1]
    name = name.lower()
    return name

def __to_file_name(name):
    return re.sub('\W', '_', name)
    

    
def __get_json(file_name):
    fHandle = open(file_name, "r" )
    jData = json.JSONDecoder().decode(fHandle.read())
    fHandle.close()
    return jData


def __set_json(file_name, json_data):
    fHandle = open(file_name,"w")
    fHandle.write(json.JSONEncoder().encode(json_data))
    fHandle.close()


def create_folder_for_person(spammer_name, person_name):
    # Create folder for person
    if not os.path.exists("logs"):
        os.makedirs("logs")
    folder_path = os.path.join(LOGS, __to_file_name(person_name))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    folder_path = os.path.join(folder_path , name_from_address(spammer_name))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Copy questions to file
    if not os.path.exists("questions.json"): # File with general questions
        raise Exception("File with questions could not be found")
    if os.path.exists(os.path.join(folder_path, "questions.json")):
        # Already exists file with questions
        return folder_path
    data = __get_json(QUESTIONS)
    random.seed()
    out_data = list()
    for list_ in data:
        out_data.append(list_[random.randint(0, len(list_) -1)])
    __set_json(os.path.join(folder_path, QUESTIONS), out_data)
    return folder_path
    

def get_question(name, person_name):
    """
    Loads file with questions and removes first one
    from this file and returns it
    """
    path = create_folder_for_person(name, person_name)
    questions = __get_json(os.path.join(path, QUESTIONS))
    if len(questions) == 0:
        return ""
    question = questions.pop()
    __set_json(os.path.join(path, QUESTIONS), questions)
    return question
    
def find_free_file(path):
    if not os.path.exists(path):
        print("ERROR: PATH doesn't exist" + path)
        raise Exception("ERROR: PATH doesn't exist" + path)
    i = 1
    while True:
        if os.path.exists(os.path.join(path, str(i))):
            i += 1
            print("File exists " + str(i))
            continue
        return os.path.join(path, str(i))
                

# print(get_question("Neil Wilson <neilw243@yahoo.com>", "1.json"))
        

p = Personas("personas2")

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
            print(message.encode('utf-8', errors='ignore'))
            print('-----------')
            # Detect language
            # Classify
            # Pick chatbot
            # print(e.get_sender()[1][0])
            reply = get_question(e.get_sender(),pers['email'])
            if len(reply) == 0:
                print(message)
                print("Out of replies")
                sys.stdin.readline()
                break # Not sure what should be here
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
