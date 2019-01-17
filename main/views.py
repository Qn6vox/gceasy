#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import render_to_response
from django.http.response import HttpResponse
from models import Record
import commands, json, logging, os, re, threading, Queue

logger = logging.getLogger("default")

def mapping(request,method):
    if not method:
        method = "index"
    return eval(method)(request)

def index(request):
    username = request.COOKIES.get("username","")
    return render_to_response("starter.html",{"username":username})

def gceasy(request):
    return render_to_response("gceasy.html")

def confissue(request):
    return render_to_response("confissue.html")

def analyze(request):
    code = 500
    msg, result, reporturl = "", "", ""
    ip = request.GET.get("targetip").strip()
    fpath = "/data/joblog/java-app-gc.log"
    tpath = "/data/joblog"
    os.system('[ ! -d %s ] && mkdir -p %s' % (tpath, tpath))
    getlog = 'rsync -e "ssh -o StrictHostKeyChecking=no" -a root@%s:%s %s/' % (ip, fpath, tpath)
    status,gclog = commands.getstatusoutput(getlog)
    logger.info(str(getlog) + " -- code:" + str(status))
    if status:
        msg = "Error: Something wrong with getlog."
    else:
        path = "%s/java-app-gc.log" % tpath
        arg = "-s -X POST --data-binary"
        apiKey = "6d79606b-28d1-4bf5-a03e-64e28b0422ea"
        contype = '--header "Content-Type:text"'
        getreport = 'curl %s @%s https://api.gceasy.io/analyzeGC?apiKey=%s %s' % (arg, path, apiKey, contype)
        status,result = commands.getstatusoutput(getreport)
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

def syn(ip, q):
    shpath = "/data/project/gceasy/main/script"
    propath = "/root/gceasy"
    os.system('[ ! -d %s ] && mkdir -p %s' % (propath, propath))
    rscmd = 'rsync -e "ssh -o StrictHostKeyChecking=no" -a %s/ root@%s:%s/' % (shpath, ip, propath)
    status, rsshell = commands.getstatusoutput(rscmd)
    logger.info(str(rscmd) + " -- code:" + str(status))
    if status:
        code = 500
        msg = "Error: Rsync conf is failed."
    else:
        shcmd = 'ssh -o StrictHostKeyChecking=no root@%s "/bin/sh /root/gceasy/iniconfig.sh"' % ip
        status, shres = commands.getstatusoutput(shcmd)
        logger.info(str(shcmd) + " -- code:" + str(status))
        if status:
            code = 500
            msg = "Error: Script execution error."
        else:
            code = 200
            msg = "Successful."
    q.put({"code":code,"ip":ip,"msg":msg})

def issue(request):
    codelist = []
    que = Queue.Queue()
    iplist = request.POST.get("iplist").strip()
    ips = re.split("[ |,|;|\t|\n]", iplist)
    logger.info(ips)
    for ip in ips:
        t = threading.Thread(target=syn, args=[ip, que])
        t.start()
    while True:
        if que.qsize() == len(ips):
            while not que.empty():
                r = que.get()
                codelist.append(r)
            logger.info(codelist)
            return HttpResponse("\n".join(["IP:%s %s" %(item["ip"],item["msg"]) for item in codelist]))