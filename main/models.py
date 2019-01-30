#coding:utf-8
from django.db import models

class Users(models.Model):
    # 用户名
    name = models.CharField(max_length=30)
    # 密码
    password = models.CharField(max_length=35)
    # 手机号
    phonenum = models.CharField(max_length=15)
    # 邮箱
    email = models.CharField(max_length=30)
    # 是否锁定
    islock = models.IntegerField(max_length=1, default=0)

class Record(models.Model):
    # 查询IP
    ip = models.GenericIPAddressField()
    # gceasy返回的报表url
    url = models.CharField(max_length=300)
    # 操作时间
    time = models.DateTimeField(auto_now_add=True)