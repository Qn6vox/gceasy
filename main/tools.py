#coding:utf-8
import logging

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