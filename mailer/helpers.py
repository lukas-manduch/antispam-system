import json
import random
import re
import os

from cleverwrap import CleverWrap
import nltk
import re
from yandex_translate import YandexTranslate

from .classifier import *

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


def to_english(message):
    # Detect language
    english_set = set(w.lower()
                        for w in nltk.corpus.words.words())
    text_set = set( w.lower() for w in
                      re.sub( '\W', ' ', message).split()
                      if w[0].isalpha() )
    unusual = text_set.difference(english_set)
    if len(unusual)*3 > len(text_set):
        print("Translating...")
        translate = YandexTranslate('trnsl.1.1.20170406T225123Z.cb036d7ebd624db9.8835c34234d938773f407ac77a601e10fc1e1771')
        message = translate.translate(message, 'en')['text'][0]
    return message

def cleverbot_reply(message):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(message)
    sentence = str()
    smallest = 10000
    for s in sentences:
        l = 50 - len(s)
        l *= l
        if smallest > l:
            sentence = s
            smallest = l
            sentence = re.sub('\W', ' ', sentence)
            print("Idenitified sentence")
            print(sentence)
            # Get CLEVERBOT reply
    cw = CleverWrap("CC1mmFptGklBB3wFbRtjhqGw7AA")
    print("Req : " + sentence)
    reply = (cw.say(sentence))
    return reply

def is_spam(db_name, message):
    if type(message) != str:
        message = message.decode('utf-8', errors='ignore')
    c = MyClassifier(db_name)
    f = Fisher(c)
    bad = (f.fisher_probability(message, "bad"))
    good = (f.fisher_probability(message, "good"))
    print(bad)
    print(good)
    return bad > good
