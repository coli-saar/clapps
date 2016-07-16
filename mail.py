import smtplib
from init import *
from flask import render_template

def send(id, recipient, subject, message):
    msg = render_template("email.txt", sender=clapps_contact, recipient=recipient, subject=subject, body=message)

    try:
        server = smtplib.SMTP(conf.get("email", "server"))
        server.starttls()
        server.login(conf.get("email", "user"), conf.get("email", "password"))
        server.sendmail(clapps_contact, recipient, msg)
        server.quit()
    except smtplib.SMTPException:
        logger.error("Error sending email to %s: id=%d, subject=%s" % (recipient, id, subject))

