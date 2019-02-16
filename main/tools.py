#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.http.response import HttpResponseRedirect
import hashlib, random

# 登录验证
class LoginCheck(object):
    @staticmethod
    def process_request(request):
        cklist = ["/register", "/resetpasswd", "/sendcode", "/resetSubmit"]
        url = request.get_full_path()
        if not (url.startswith("/login") or url in cklist):
            logged = request.session.get("logged",False)
            if not logged:
                redirect = "/login?url=%s" % url
                return HttpResponseRedirect(redirect)

# md5加密
def enpasswd(ps):
    md5 = hashlib.md5(bytes('adc'.encode('utf-8')))
    md5.update(bytes(ps.encode('utf-8')))
    return md5.hexdigest()

# 生成随机验证码
def captcha(randomlength=8):
    code = ""
    chars = "abcdefghijklmnpqrstuvwsyzABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
    length = len(chars) - 1
    for i in range(randomlength):
        code += chars[random.randint(0, length)]
    return code