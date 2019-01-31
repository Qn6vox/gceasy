#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(receivers, sub, content, ct='plain', attach=None):
    mailhost = "dwmail.dangdang.com"
    mailuser = "ddop"
    mailpass = "5GxIQSdGcV"
    mailpostfix = "dangdang.com"
    me = "hello" + "<" + mailuser + "@" + mailpostfix + ">"
    msg = MIMEText(content, _subtype=ct, _charset='utf-8')
    if attach:
        mtp = MIMEMultipart()
        mtp.attach(msg)
        mtp.attach(attach)
        msg = mtp
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(receivers)

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mailhost)
        smtpObj.starttls()
        smtpObj.login(mailuser, mailpass)
        smtpObj.sendmail(me, receivers, msg.as_string())
        smtpObj.close()
        return True
    except smtplib.SMTPException, e:
        print str(e)
        return False