import email
import re
import requests
import os
from requests.auth import AuthBase
from email.utils import getaddresses
import logging
import sys
import config
import json
from email_reply_parser import EmailReplyParser
import quopri
import HTMLParser
from flufl.bounce import all_failures, scan_message

logging.basicConfig(filename='mailing_logger.txt', level=logging.INFO)

class ApiKeyAuth(AuthBase):
    """
    Sets the appropriate authentication headers
    for the Tastypie API key authentication.
    """
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def __call__(self, r):
        r.headers['Authorization'] = 'ApiKey %s:%s' % (self.username, self.api_key)
        return r

class EmailAnswer(object):
    def __init__(self):
        self.subject = ''
        self._content_text = ''
        self.outbound_message_identifier = ''
        self.email_from = ''
        self.when = ''
        self.requests_session = requests.Session()
        username = config.WRITEIT_USERNAME
        apikey = config.WRITEIT_API_KEY
        self.requests_session.auth = ApiKeyAuth(username, apikey)
        self.is_bounced = False

    def get_content_text(self):
        cleaned_content = self._content_text
        pattern = '[\w\.-]+@[\w\.-]+'
        expression = re.compile(pattern)
        # cleaned_content = re.sub(expression, '', cleaned_content)
        cleaned_content = re.sub(r'[\w\.-\.+]+@[\w\.-]+','', cleaned_content)


        cleaned_content = cleaned_content.replace(self.outbound_message_identifier, '')
        return cleaned_content

    def set_content_text(self, value):
        self._content_text = value

    content_text = property(get_content_text, set_content_text)



    def save(self):
        data = {
        'key': self.outbound_message_identifier,
        'content': self.content_text,
        'format' :'json'
        }
        headers = {'content-type': 'application/json'}
        result = self.requests_session.post(config.WRITEIT_API_ANSWER_CREATION, data=json.dumps(data), headers=headers)
        log = "When sent to %(location)s the status code was %(status_code)d"
        log = log % {
            'location':config.WRITEIT_API_ANSWER_CREATION,
            'status_code':result.status_code
            }
        logging.info(log)

    def send_back(self):
        if self.is_bounced:
            self.report_bounce()
        else:
            self.save()

    def report_bounce(self):
        data = {
        'key':self.outbound_message_identifier
        }
        headers = {'content-type': 'application/json'}
        result = self.requests_session.post(config.WRITEIT_API_WHERE_TO_REPORT_A_BOUNCE, data=json.dumps(data), headers=headers)

class EmailHandler():
    def __init__(self, answer_class=EmailAnswer):
        self.message = None
        self.answer_class = answer_class

    def handle(self, lines):
        answer = self.answer_class()
        msgtxt = ''.join(lines)

        msg = email.message_from_string(msgtxt)
        temporary, permanent = all_failures(msg)
        
        
        if temporary or permanent:
            answer.is_bounced = True
            answer.email_from = scan_message(msg).pop()
        else:
            answer.email_from = msg["From"]


        the_recipient = msg["To"]
        answer.subject = msg["Subject"]
        answer.when = msg["Date"]

        the_recipient = re.sub(r"\n", "", the_recipient)

        regex = re.compile(r".*[\+\-](.*)@.*")

        answer.outbound_message_identifier = regex.match(the_recipient).groups()[0]
        charset = msg.get_charset()
        logging.info("Reading the parts")
        for part in msg.walk():
            logging.info("Part of type "+part.get_content_type())
            if part.get_content_type() == 'text/plain':
                charset = part.get_content_charset()
                if not charset:
                    charset = "ISO-8859-1"
                data = part.get_payload(decode=True).decode(charset)
                text = EmailReplyParser.parse_reply(data)
                text.strip()
                answer.content_text = text
        #logging stuff
        
        log = 'New incoming email from %(from)s sent on %(date)s with subject %(subject)s and content %(content)s'
        log = log % {
            'from':answer.email_from,
            'date':answer.when,
            'subject':answer.subject,
            'content':answer.content_text
            }
        logging.info(log)
        return answer









if __name__ == '__main__': # pragma: no cover
    lines = sys.stdin.readlines()
    handler = EmailHandler()
    answer = handler.handle(lines)
    answer.send_back()
    sys.exit(0)