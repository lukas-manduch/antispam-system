from email import *
import base64

class EmlParser:
    def __init__(self, eml_content):
        parser = feedparser.FeedParser()
        parser.feed(eml_content)
        self.msg = parser.close()
        self.plain = str()
        self._parse_body()

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
