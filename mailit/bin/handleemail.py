import email
import re
import requests
from requests.auth import AuthBase
import logging
import sys
import config
import json
from email_reply_parser import EmailReplyParser
from flufl.bounce import all_failures, scan_message
from mailit.models import RawIncomingEmail
from nuntium.models import Answer

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


class EmailReportBounceMixin(object):
    def report_bounce(self):
        data = {'key': self.outbound_message_identifier}
        headers = {'content-type': 'application/json'}
        self.requests_session.post(
            config.WRITEIT_API_WHERE_TO_REPORT_A_BOUNCE,
            data=json.dumps(data),
            headers=headers,
            )


class EmailSaveMixin(object):
    def save(self):
        data = {
            'key': self.outbound_message_identifier,
            'content': self.content_text,
            'format': 'json',
            }
        headers = {'content-type': 'application/json'}
        result = self.requests_session.post(config.WRITEIT_API_ANSWER_CREATION, data=json.dumps(data), headers=headers)
        log = "When sent to %(location)s the status code was %(status_code)d"
        log = log % {
            'location': config.WRITEIT_API_ANSWER_CREATION,
            'status_code': result.status_code,
            }
        logging.info(log)
        answer = None
        try:
            answer_id = json.loads(result.content)['id']
            answer = Answer.objects.get(id=answer_id)
        except Exception:
            pass
        return answer


class EmailAnswer(EmailSaveMixin, EmailReportBounceMixin):
    def __init__(self):
        self.subject = ''
        self._content_text = ''
        self.content_html = ''
        self.outbound_message_identifier = ''
        self.email_from = ''
        self.when = ''
        self.message_id = None  # http://en.wikipedia.org/wiki/Message-ID
        self.requests_session = requests.Session()
        username = config.WRITEIT_USERNAME
        apikey = config.WRITEIT_API_KEY
        self.requests_session.auth = ApiKeyAuth(username, apikey)
        self.is_bounced = False

    def get_content_text(self):
        cleaned_content = self._content_text
        # pattern = '[\w\.-]+@[\w\.-]+'
        # expression = re.compile(pattern)
        # cleaned_content = re.sub(expression, '', cleaned_content)
        cleaned_content = re.sub(r'[\w\.-\.+]+@[\w\.-]+', '', cleaned_content)

        cleaned_content = cleaned_content.replace(self.outbound_message_identifier, '')
        return cleaned_content

    def set_content_text(self, value):
        self._content_text = value

    content_text = property(get_content_text, set_content_text)

    def send_back(self):
        if self.is_bounced:
            self.report_bounce()
        else:
            answer = self.save()
            raw_answers = RawIncomingEmail.objects.filter(message_id=self.message_id)
            if answer is not None and raw_answers:
                raw_email = raw_answers[0]
                raw_email = RawIncomingEmail.objects.get(message_id=self.message_id)
                raw_email.answer = answer
                raw_email.save()


class EmailHandler():
    def __init__(self, answer_class=EmailAnswer):
        self.message = None
        self.answer_class = answer_class
        self.content_types_parsers = {
            'text/plain': self.parse_text_plain
        }

    def save_raw_email(self, lines):
        raw_email = RawIncomingEmail.objects.create(content=lines)
        return raw_email

    def instanciate_answer(self, lines):
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
        answer.message_id = msg["Message-ID"]

        the_recipient = re.sub(r"\n", "", the_recipient)

        regex = re.compile(r".*[\+\-](.*)@.*")

        answer.outbound_message_identifier = regex.match(the_recipient).groups()[0]
        logging.info("Reading the parts")
        for part in msg.walk():
            logging.info("Part of type " + part.get_content_type())
            processed = False
            if part.get_content_type() in self.content_types_parsers.keys():
                answer = self.content_types_parsers[part.get_content_type()](answer, part)
                processed = True

            if not processed:
                self.handle_not_processed_part(part)
        #logging stuff

        log = 'New incoming email from %(from)s sent on %(date)s with subject %(subject)s and content %(content)s'
        log = log % {
            'from': answer.email_from,
            'date': answer.when,
            'subject': answer.subject,
            'content': answer.content_text,
            }
        logging.info(log)
        return answer

    def parse_text_plain(self, answer, part):
        charset = part.get_content_charset()
        if not charset:
            charset = "ISO-8859-1"
        data = part.get_payload(decode=True).decode(charset)
        text = EmailReplyParser.parse_reply(data)
        text.strip()
        answer.content_text = text
        return answer

    def handle_not_processed_part(self, part):
        pass

    def set_raw_email_with_processed_email(self, raw_email, email_answer):
        raw_email.message_id = email_answer.message_id
        raw_email.save()

    def handle(self, lines):
        raw_email = self.save_raw_email(lines)
        email_answer = self.instanciate_answer(lines)
        self.set_raw_email_with_processed_email(raw_email, email_answer)

        return email_answer


if __name__ == '__main__':  # pragma: no cover
    lines = sys.stdin.readlines()
    handler = EmailHandler()
    answer = handler.handle(lines)
    answer.send_back()
    sys.exit(0)
