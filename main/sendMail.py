#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json, smtplib, os, requests, commands
from email.mime.text import MIMEText

def sendMail(content):
    mailhost = "dwmail.dangdang.com"
    mailuser = "ddop"
    mailpass = "5GxIQSdGcV"
    sender = 'ddop@dangdang.com'

    host = os.popen("/sbin/ifconfig|grep -A1 eth[01]|grep -m1 inet|awk -F: '{printf $2}'|awk '{printf $1}'").readline()
    addrlist = requests.get("http://dtree.pe.api/getContact?host=%s" % host)
    addrs = json.loads(addrlist.text)
    receivers = []
    for addr in addrs["contacts"]:
        receivers.append(addr["email"])

    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = "GC 报警邮件"
    msg['From'] = "ddop@dangdang.com"
    msg['To'] = ";".join(receivers)

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mailhost)
        smtpObj.starttls()
        smtpObj.login(mailuser, mailpass)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        smtpObj.close()
        return True
    except smtplib.SMTPException, e:
        print(e)
        return False

if __name__ == '__main__':
    path = "/data/gceasy/jvm.log"
    cmd = 'curl -s -X POST --data-binary @%s http://api.gceasy.io/analyzeGC?apiKey=6d79606b-28d1-4bf5-a03e-64e28b0422ea --header "Content-Encoding:zip"' % path
    status, result = commands.getstatusoutput(cmd)
    data = json.loads(result)
    state = data["isProblem"]

    if state:
        detail = data["problem"]
        me = "\n".join(detail)
        sendMail(me)