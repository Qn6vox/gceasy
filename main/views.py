#coding:utf-8
from django.shortcuts import render_to_response
from django.http.response import HttpResponse
import commands, time, json, webbrowser
import logging

logger = logging.getLogger("default")

# Create your views here.
def mapping(request,method):
    if not method:
        method = "index"
    return eval(method)(request)

def index(request):
    #从cookie获取当前登陆的帐户
    username = request.COOKIES.get("username","")
    return render_to_response("starter.html",{"username":username})

def gceasy(request):
    time.sleep(1)
    return render_to_response("gceasy.html")

def analyze(request):
    path = request.GET.get("path").strip()
    cmd = 'curl -s -X POST --data-binary @%s http://api.gceasy.io/analyzeGC?apiKey=6d79606b-28d1-4bf5-a03e-64e28b0422ea --header "Content-Encoding:zip"' % path
    status,result = commands.getstatusoutput(cmd)
    logger.info(cmd)
    logger.info(result)
    gurl = json.loads(result)
    url = gurl["graphURL"]
    return HttpResponse(url)
