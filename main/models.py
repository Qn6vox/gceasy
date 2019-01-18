#coding:utf-8
from django.db import models

class Record(models.Model):
    #查询IP
    ip = models.GenericIPAddressField()
    #gceasy返回的报表url
    url = models.CharField(max_length=300)
    #操作时间
    time = models.DateTimeField(auto_now_add=True)