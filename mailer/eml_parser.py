from email import *
import base64
import chardet


def get_text(msg):
    """ Parses email message text, given message object
    This doesn't support infinite recursive parts, but mail is usually not so naughty.
    """
    text = ""
    print("Get text")
    if msg.is_multipart():
        print("Is multipart")
        html = None
        for part in msg.get_payload():
            print(part.get_content_type())
            if part.get_content_type() == 'text/plain':
                text = part.get_payload(decode=True)
            if part.get_content_type() == 'text/html':
                html = part.get_payload(decode=True)
            if part.get_content_type() == 'multipart/alternative':
                for subpart in part.get_payload():
                    if subpart.get_content_type() == 'text/plain':
                        text = subpart.get_payload(decode=True)
                    if subpart.get_content_type() == 'text/html':
                        html = subpart.get_payload(decode=True)

        if text is None:
            return html.strip()
        else:
            return text.strip()
    else:
        text = msg.get_payload(decode=True)
        return text.strip()

    
def parse_body(message): # returns tuple plain + html
    plain = bytes()
    html = bytes()
    if type(message) == str:
        return message.encode('utf-8') , b''
    if message.is_multipart():
        print("is multipart")
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
    print(ct)
    if ct.find('html')!= -1:
        html = message.get_payload(decode=True)
    elif ct.find('plain') != -1:
        plain = message.get_payload(decode=True)
        print(plain)
    elif ct.find('alternative') != -1:
        for payl in message.get_payload():
            if payl.get_content_type() == 'text/plain':
                plain += payl.get_payload(decode=True)
    return plain , html


class EmlParser:
    def __init__(self, eml_content):
        parser = feedparser.FeedParser()
        parser.feed(eml_content.decode('utf-8'))
        self.msg = parser.close()
        self.plain = bytes()
        self.content = bytes()
        self.plain , self.content = parse_body(self.msg)
        # self.plain = get_text(self.msg)

        
    def _parse_body(self) -> str:
        self.content = str()
        if self.msg.is_multipart():
            for payload in self.msg.get_payload():
                if (payload['Content-Type'] != None and
                    payload['Content-Type'].find('plain') != -1):
                    # found plain text this is best case
                    self.plain = payload.get_payload()
                    return # Plain is best scenario
                self.content += (payload.get_payload())
        else:
            self.content += (self.msg.get_payload())
        # Not very effective check if content is not base64ed
        try:
            if self.msg['Content-Transfer-Encoding'].lower() == "base64":
                self.content = str(base64.b64decode(self.content))
        except:
            pass

    def get_body(self) -> str:
        if len(self.plain) != 0:
            return self.plain
        return self.content

    def get_from_address(self) -> str:
        if self.msg['Reply-to'] != None:
            return self.msg['Reply-to']
        return self.msg['From']

    def get_sender(self):
        return self.msg['From']

    def get_subject(self):
        return self.msg['Subject']

    def get_date(self):
        return self.msg['Date']
