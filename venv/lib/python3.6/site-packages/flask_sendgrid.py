# -*- coding: utf-8 -*-
"""
    flask_sendgrid
    ~~~~
    Adds SendGrid support to Flask applications
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SGMail
from sendgrid.helpers.mail import Email, Content, Personalization


__version__ = '0.7.1'
__versionfull__ = __version__


class SendGrid(SGMail):
    app = None
    api_key = None
    client = None
    default_from = None

    def __init__(self, app=None, **opts):
        if app:
            self.init_app(app)
        super(SGMail, self).__init__()
        self.from_email = None
        self.subject = None
        self._personalizations = None
        self._contents = None
        self._attachments = None
        self._template_id = None
        self._sections = None
        self._headers = None
        self._categories = None
        self._custom_args = None
        self._send_at = None
        self._batch_id = None
        self._asm = None
        self._ip_pool_name = None
        self._mail_settings = None
        self._tracking_settings = None
        self._reply_to = None

    def init_app(self, app):
        self.app = app
        self.api_key = app.config['SENDGRID_API_KEY']
        self.default_from = app.config['SENDGRID_DEFAULT_FROM']
        self.client = SendGridAPIClient(self.api_key).client

    def send_email(self, to_email, subject, from_email=None, html=None, text=None, *args, **kwargs):  # noqa
        if not any([from_email, self.default_from]):
            raise ValueError("Missing from email and no default.")
        if not any([html, text]):
            raise ValueError("Missing html or text.")

        self.from_email = Email(from_email or self.default_from)
        self.subject = subject

        personalization = Personalization()

        if type(to_email) is list:
            for email in self._extract_emails(to_email):
                personalization.add_to(email)
        elif type(to_email) is Email:
            personalization.add_to(to_email)
        elif type(to_email) is str:
            personalization.add_to(Email(to_email))

        self.add_personalization(personalization)

        content = Content("text/html", html) if html else Content("text/plain", text)
        self.add_content(content)

        return self.client.mail.send.post(request_body=self.get())

    def _extract_emails(self, emails):
        if type(emails[0]) is Email:
            for email in emails:
                yield email
        elif type(emails[0]) is dict:
            for email in emails:
                yield Email(email['email'])
