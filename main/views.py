#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import render_to_response
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from models import Users, Record
from tools import enpasswd, captcha
from ldapUtils import ldapLogin
from sendMail import sendMail
from ansibleApi import ansibleApi
import commands, json, logging, os, re, threading, Queue

logger = logging.getLogger("default")

def mapping(request, method):
    if not method:
        method = "login"
    return eval(method)(request)

# 登录
def login(request):
    if request.method == "GET":
        return render_to_response("login.html")

    username = request.POST.get("username", "")
    passwd = request.POST.get("passwd", "")
    code = 500

    # ldap登录校验
    logged, msg = ldapLogin(username, passwd)
    logger.info(str(username) + " " + str(msg))
    if logged:
        code = 200
        request.session["logged"] = True
        request.session["username"] = username
    url = request.session.get("url", "/index")

    # 普通登录校验
    # try:
    #     Users.objects.get(name=username, password=enpasswd(passwd))
    #     code = 200
    #     request.session["logged"] = True
    #     request.session["username"] = username
    #     url = request.session.get("url", "/index")
    # except Users.DoesNotExist:
    #     msg = "用户名或密码错误，请重新输入"
    #     url = request.session.get("url", "/")

    return HttpResponse(json.dumps({"code": code, "msg": msg, "url":url}))

# 登出
def logout(request):
    request.session["logged"] = False
    return HttpResponseRedirect('/login')

# 注册
def register(request):
    if request.method == "GET":
        return render_to_response("register.html")

    username = request.POST.get("username", "")
    passwd = request.POST.get("passwd", "")
    phonenum = request.POST.get("phonenum", "")
    email = request.POST.get("email", "")
    try:
        Users.objects.get(name=username)
        code = 500
        msg = "用户名已被注册，请重新注册"
        url = ""
    except Users.DoesNotExist:
        Users(name=username, password=enpasswd(passwd), phonenum=phonenum, email=email).save()
        code = 200
        msg = "注册成功，请登录"
        url = "/login"
    logger.info(str(username) + " " + str(msg))
    return HttpResponse(json.dumps({"code": code, "msg": msg, "url": url}))

# 重置密码
def resetpasswd(request):
    return render_to_response("resetpasswd.html")

def sendcode(request):
    username = request.POST.get("username", "")
    email = request.POST.get("email", "")
    code = 500
    vecode = captcha(5)
    request.session["vecode"] = vecode
    try:
        Users.objects.get(name=username, email=email)
        sendMail([email], "重置密码验证码", vecode)
        code = 200
        msg = "验证码已发送至邮箱"
    except Users.DoesNotExist:
        msg = "验证信息错误，请重新输入"
    logger.info(str(email) + " " + str(msg))
    return HttpResponse(json.dumps({"code": code, "msg": msg}))

def resetSubmit(request):
    username = request.POST.get("username", "")
    ckcode = request.POST.get("captcha", "")
    passwd = request.POST.get("passwd", "")
    code = 500
    vecode = request.session.get("vecode", "")
    if ckcode == vecode:
        user = Users.objects.get(name=username)
        user.password = enpasswd(passwd)
        user.save()
        code = 200
        msg = "密码重置成功，请重新登录"
        url = "/login"
    else:
        msg = "验证码错误，请重新输入"
        url = ""
    logger.info(str(username) + " " + str(msg))
    return HttpResponse(json.dumps({"code": code, "msg": msg, "url": url}))

# 首页
def index(request):
    username = request.session.get("username", "")
    return render_to_response("starter.html", {"username":username})

# 配置分发
def confissue(request):
    return render_to_response("confissue.html")

def sync(ip, q, appname):
    shpath = "/data/project/gceasy/main/script"
    propath = "/root/gceasy/%s" % appname
    os.system('ssh -o StrictHostKeyChecking=no root@%s "[ %s ] && mkdir -p %s"' % (ip, propath, propath))
    rscmd = 'rsync -e "ssh -o StrictHostKeyChecking=no" -a %s/ root@%s:%s/' % (shpath, ip, propath)
    status, rsshell = commands.getstatusoutput(rscmd)
    logger.info(str(rscmd) + " -- code:" + str(status))
    if status:
        code = 500
        msg = "Error: Rsync conf is failed."
    else:
        shcmd = 'ssh -o StrictHostKeyChecking=no root@%s "/bin/sh %s/setopts.sh %s"' % (ip, propath, appname)
        status, shres = commands.getstatusoutput(shcmd)
        logger.info(str(shcmd) + " -- code:" + str(status))
        if status:
            code = 500
            msg = "Error: Script execution error."
        else:
            code = 200
            msg = "Successful."
    q.put({"code": code, "ip": ip, "msg": msg})

def issue(request):
    codelist = []
    q = Queue.Queue()
    iplist = request.POST.get("iplist").strip()
    appname = request.POST.get("appname").strip()
    ips = re.split("[,;\t\n ]", iplist)
    logger.info("issueips:" + str(ips))
    for ip in ips:
        t = threading.Thread(target=sync, args=[ip, q, appname])
        t.start()
    while True:
        if q.qsize() == len(ips):
            while not q.empty():
                r = q.get()
                codelist.append(r)
            logger.info(codelist)
            return HttpResponse("\n".join(["IP: %s %s" % (item["ip"], item["msg"]) for item in codelist]))

# 日志分析
def gceasy(request):
    return render_to_response("gceasy.html")

def searchapp(request):
    code = 200
    msg = ""
    ip = request.GET.get("targetip").strip()
    os.system("ssh -o StrictHostKeyChecking=no root@%s" % ip)
    getapp = "ssh -o StrictHostKeyChecking=no root@%s \"ls -l /usr/local |awk '{print \$9}' |grep \"tomcat*\"\"" % ip
    status, result = commands.getstatusoutput(getapp)
    if status:
        code = 500
        msg = "Error: Get applist falied."
    applist = []
    for app in result.split():
        applist.append(app)
    logger.info(str(ip) + " -- applist=" + str(applist))
    return HttpResponse(json.dumps({"code": code, "msg": msg, "applist":applist}))

def analyze(request):
    code = 500
    msg, result, reporturl = "", "", ""
    ip = request.GET.get("targetip").strip()
    appname = request.GET.get("appname").strip()
    stime = request.GET.get("starttime", "").strip()
    etime = request.GET.get("endtime", "").strip()
    confpath = "/root/gceasy/%s/logpath.conf" % appname
    getpath = "ssh -o StrictHostKeyChecking=no root@%s \"awk '/path/ {print}' %s\"" % (ip, confpath)
    try:
        fpath = commands.getoutput(getpath).split("=")[1]
    except IndexError:
        msg = "Error: Something wrong with ip or appname."
        return HttpResponse(json.dumps({"code": code, "msg": msg}))
    tpath = "/data/joblog"
    os.system('[ %s ] && mkdir -p %s' % (tpath, tpath))
    getlog = 'rsync -e "ssh -o StrictHostKeyChecking=no" -a root@%s:%s %s/' % (ip, fpath, tpath)
    status, gclog = commands.getstatusoutput(getlog)
    logger.info(str(getlog) + " -- code:" + str(status))
    if status:
        msg = "Error: Something wrong with getlog."
    else:
        path = "%s/gc-%s.log" % (tpath, appname)
        arg = "-s -X POST --data-binary"
        apiKey = "6d79606b-28d1-4bf5-a03e-64e28b0422ea"
        contype = '--header "Content-Type:text"'
        if stime == etime == "":
            getreport = 'curl %s @%s https://api.gceasy.io/analyzeGC?apiKey=%s %s' % (arg, path, apiKey, contype)
        else:
            st = "%sT00%%3A00%%3A00.000-0700" % stime
            et = "%sT24%%3A00%%3A00.000-0700" % etime
            getreport = 'curl %s @%s https://api.gceasy.io/analyzeGC?apiKey=%s&startTime=%s&endTime=%s' % (arg, path, apiKey, st, et)
        status, result = commands.getstatusoutput(getreport)
        logger.info(getreport)
        logger.info(result)
        data = json.loads(result)
        if "graphURL" not in data.keys():
            msg = "Error: Something wrong with report."
        else:
            reporturl = data["graphURL"]
            Record(ip=ip, url=reporturl).save()
            code = 200
    return HttpResponse(json.dumps({"code":code, "msg":msg, "reporturl":reporturl, "result":result}))

# 历史记录
def hisrecord(request):
    records = Record.objects.all()
    return render_to_response("hisrecord.html", {"records":records})

def checkhis(request):
    checkip = request.GET.get("checkip", "").strip()
    stime = request.GET.get("starttime", "").strip()
    etime = request.GET.get("endtime", "").strip()
    logger.info("checkrecordip:" + str(checkip) + " starttime:" + str(stime) + " endtime:" + str(etime))
    if stime == etime == "":
        records = Record.objects.filter(ip=checkip)
    elif stime == etime:
        records = Record.objects.filter(Q(ip=checkip), Q(time__gt=stime, time__lt="%s 23:59:59" % etime))
    else:
        records = Record.objects.filter(Q(ip=checkip), Q(time__gt="%s 23:59:59" %stime, time__lt=etime))
    return render_to_response("hisrecord.html", {"records":records, "checkip":checkip})

# 应用监控
def javamonitor(request):
    return render_to_response("javamonitor.html")

def setagent(request):
    iplist = request.POST.get("iplist").strip()
    ips = re.split("[,;\t\n ]", iplist)
    logger.info("setagent iplist: " + str(ips))
    agentpath = "/data/project/gceasy/main/javamonitor"
    tgpath = "/root/javamonitor"
    ansibleApi(ips).ansible("shell", "[ %s ] && mkdir -p %s" % (tgpath, tgpath))
    status, msg, results = ansibleApi(ips).ansible("copy", "src=%s/ dest=%s/ mode=0755" % (agentpath, tgpath))
    #status, msg, results = ansibleApi(ips).ansible("shell", "./%s/client" % tgpath)
    code = 500
    logger.info("Ansible play status: " + str(status))
    logger.info(results)
    if status:
        code = 200
    return HttpResponse(json.dumps({"code": code, "msg": msg}))