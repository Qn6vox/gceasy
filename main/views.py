#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import render_to_response
from django.http.response import HttpResponse
import commands, json, logging

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
    path = request.GET.get("path").strip()
    cmd = 'curl -s -X POST --data-binary @%s http://api.gceasy.io/analyzeGC?apiKey=6d79606b-28d1-4bf5-a03e-64e28b0422ea --header "Content-Type:text"' % path
    status,result = commands.getstatusoutput(cmd)
    logger.info(cmd)
    logger.info(result)
    gurl = json.loads(result)
    reporturl = gurl["graphURL"]
    return HttpResponse(json.dumps({"reporturl":reporturl, "result":result}))