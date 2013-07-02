#! /usr/bin/env python
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

class EmailHandler():
    def __init__(self):
        self.message = None

    def handle(self, lines):
        
        answer = EmailAnswer()
        msgtxt = ''
        for line in lines:
            msgtxt += str(line)

        msg = email.message_from_string(msgtxt)
        answer.subject = msg["Subject"]
        answer.email_from = msg["From"]
        answer.when = msg["Date"]
        regex = re.compile(r".*[\+\-](.*)@.*")

        answer.outbound_message_identifier = regex.match(msg["To"]).groups()[0]

        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                answer.content_text = EmailReplyParser.parse_reply(part.get_payload(decode=True))
                answer.content_text.strip()
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


class EmailAnswer():
    def __init__(self):
        self.subject = ''
        self.content_text = ''
        self.outbound_message_identifier = ''
        self.email_from = ''
        self.when = ''
        self.requests_session = requests.Session()
        username = config.WRITEIT_USERNAME
        apikey = config.WRITEIT_API_KEY
        self.requests_session.auth = ApiKeyAuth(username, apikey)




    def send_back(self):
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

if __name__ == '__main__': # pragma: no cover
    lines = sys.stdin.readlines()
    handler = EmailHandler()
    answer = handler.handle(lines)
    answer.send_back()
    sys.exit(0)