#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import hashlib, logging
from django.http.response import HttpResponseRedirect

logger = logging.getLogger("default")

#定义一个用来判断是否登陆的中间件
class LoginCheck():
    def process_request(self,request):
        try:
            #判断是否已登陆的条件是cookie中是否有username
            request.COOKIES['username']
        #如果cookie中没有username，则跳转去登陆
        except Exception:
            #获取当前访问的域名和uri
            host = request.get_host()
            uri = request.get_full_path()
            return HttpResponseRedirect('http://dtree.pe.dapp.com/login?uri=http://%s%s' % (host,uri))

# md5加密
def enpasswd(ps):
    md5 = hashlib.md5(bytes('adc'.encode('utf-8')))
    md5.update(bytes(ps.encode('utf-8')))
    return md5.hexdigest()