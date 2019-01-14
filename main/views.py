#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import render_to_response
from django.http.response import HttpResponse
import commands, json, logging, os, sys

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

def analyze(request):
    ip = request.GET.get("targetip").strip()
    fpath = "/data/joblog/java-app-gc.log"
    tpath = "/data/joblog"
    getlog = os.system('rsync -e "ssh -o StrictHostKeyChecking=no" root@%s:%s %s/ > /dev/null 2>&1' % (ip, fpath, tpath))
    if getlog:
        print "Error: Something wrong with getlog."
        sys.exit(0)
    getcode = 'curl -I -m 3 -o /dev/null -s -w %{http_code} https://api.gceasy.io'
    code = commands.getoutput(getcode)
    if int(code) != 200:
        print "Error: Something wrong with gceasy."
        sys.exit(0)
    path = "%s/java-app-gc.log" % tpath
    apiKey = "6d79606b-28d1-4bf5-a03e-64e28b0422ea"
    ctype = '--header "Content-Type:text"'
    getreport = 'curl -s -X POST --data-binary @%s https://api.gceasy.io/analyzeGC?apiKey=%s %s' % (path, apiKey, ctype)
    status,result = commands.getstatusoutput(getreport)
    logger.info(getreport)
    logger.info(result)
    data = json.loads(result)
    if "graphURL" not in data.keys():
        print "Error: Something wrong with report."
        sys.exit(0)
    reporturl = data["graphURL"]
    return HttpResponse(json.dumps({"reporturl":reporturl, "result":result}))