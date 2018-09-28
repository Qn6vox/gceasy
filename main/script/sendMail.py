#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json, smtplib, os, requests, commands, ConfigParser, sys
from email.mime.text import MIMEText

def sendMail(content):
    mailhost = "dwmail.dangdang.com"
    mailuser = "ddop"
    mailpass = "*"
    sender = 'ddop@dangdang.com'

    os7 = os.system('/bin/cat /etc/redhat-release | grep " 7.*"' + '> /dev/null 2>&1')
    if os7 == 0:
        iface = os.popen("/sbin/route -n|awk '{if($4~/UG/){print $8}}'|head -n 1").read().strip('\n')
        getip = "/sbin/ip a|grep -B1 -C1 -w %s|grep -w inet|awk '{printf $2}'|awk -F '/' '{printf $1}'" % iface
        host = os.popen(getip).readline()
    else:
        host = os.popen("/sbin/ifconfig|grep -A1 eth[01]|grep -m1 inet|awk -F: '{printf $2}'|awk '{printf $1}'").readline()

    addrlist = requests.get("http://dtree.pe.api/getContact?host=%s" % host)
    addrs = json.loads(addrlist.text)
    receivers = []
    for addr in addrs["contacts"]:
        receivers.append(addr["email"])

    if len(receivers) == 0:
        try:
            sys.exit(0)
        except SystemExit:
            print("未获取到收件人信息")

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

def getValues(section, option):
    currDir = os.path.dirname(os.path.realpath(__file__))
    confPath = currDir + os.sep + "logpath.conf"
    config = ConfigParser.SafeConfigParser()
    config.read(confPath)
    return config.get(section=section, option=option)

if __name__ == '__main__':
    path = getValues('source', 'path')
    cmd = 'curl -s -X POST --data-binary @%s http://api.gceasy.io/analyzeGC?apiKey=6d79606b-28d1-4bf5-a03e-64e28b0422ea --header "Content-Type:text"' % path
    status, result = commands.getstatusoutput(cmd)
    data = json.loads(result)
    state = data["isProblem"]

    if state:
        detail = data["problem"]
        me = "\n".join(detail)
        sendMail(me)