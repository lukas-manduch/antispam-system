from email import *
from email.header import decode_header
from bs4 import BeautifulSoup
from markdown import markdown
import base64
import chardet
import re



def parse_body(message): # returns tuple plain + html
    plain = bytes()
    html = bytes()
    if type(message) == str:
        return message.encode('utf-8') , b''
    if message.is_multipart():
        for payl in message.get_payload():
            plain_, html_ = parse_body(payl)
            if len(plain_) > 0:
                plain += (plain_)
            if len(html_):
                html += (html_)
        return plain, html
    if message.get_filename(): # is it attachment?
        return plain, html
    ct = message.get_content_type()
    if ct.find('html')!= -1:
        html = message.get_payload(decode=True)
    elif ct.find('plain') != -1:
        plain = message.get_payload(decode=True)
    elif ct.find('alternative') != -1:
        for payl in message.get_payload():
            if payl.get_content_type() == 'text/plain':
                plain += payl.get_payload(decode=True)
    return plain , html

def header_utf(header):
    arr = decode_header(header)
    out = str()
    for part in arr:
        if type(part[0]) == bytes:
            out += part[0].decode('utf-8', errors='ignore')
        else:
            out += part[0]
    return out

class EmlParser:
    def __init__(self, eml_content):
        parser = feedparser.FeedParser()
        parser.feed(eml_content.decode('utf-8', errors='ignore'))
        self.msg = parser.close()
        self.plain = bytes()
        self.content = bytes()
        self.plain , self.content = parse_body(self.msg)


    def get_body(self):
        # Returns plain and html parts
        return self.plain, self.content

    def get_from_address(self):
        if self.msg['Reply-to'] != None:
            return self.msg['Reply-to']
        return self.msg['From']

    def get_sender(self):
        return header_utf(self.msg['From'])

    def get_subject(self):
        return header_utf(self.msg['Subject'])

    def get_date(self):
        return header_utf(self.msg['Date'])

    def get_context(self):
        # Returns content as plain text
        if len(self.plain) != 0:
            return self.plain
        m = markdown(self.content)
        return ''.join(BeautifulSoup(m,
                                     "lxml").findAll(text=True))
        
