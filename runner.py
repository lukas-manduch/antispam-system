
from mailer.personas import *
from mailer.imap import *
from mailer.eml_parser import *
from mailer.smtp import Smtp


from cleverwrap import CleverWrap
import nltk
import re
from email_reply_parser import *
from yandex_translate import YandexTranslate



def form_reply(from_, date, subject, message):
    return "\n\n---------- Original Message ----------\n" \
        "From: %s\nDate: %s\nSubject: %s\n\n%s" % (from_,
                                                 date,
                                                 subject,
                                                 message)


p = Personas(".\personas")

# cw = CleverWrap("CC1mmFptGklBB3wFbRtjhqGw7AA")
# print(cw.say("Hello"))

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
            # Classify
            if e.get_subject().lower().find("re:") == -1:
                # Use classifier
                pass
            # Pick chatbot
            if message.lower().find("address") != -1:
                reply = "Here are data you requested\n" \
                        "%s\n%s\n%s" % (pers['name'] + " " +
                                        pers['surname'],
                                        pers['address'],
                                        pers['email'])
            else:
                print("Using CLEVERBOT")
                # Pick sentence to reply to
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
