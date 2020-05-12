from flask_mail import Mail, Message
from app import app

mail = Mail(app)

def sendmail(subject, sender, recipient, body):
    try:
        msg = Message(subject, sender=sender, recipients=[recipient])
        msg.body = body
        mail.send(msg)
        return "Sent"
    except Exception as e:
        return e