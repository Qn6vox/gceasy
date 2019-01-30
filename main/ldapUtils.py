#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ldap
from models import Users
import logging

logger = logging.getLogger("info")

ldappath = "ldap://192.168.80.10" #ldap服务器地址
baseDN = "ou=KeWenDangDang,dc=dangdang,dc=com" #根目录
ldapuser = "adsmart@dangdang.com" #ldap服务器用户名
ldappass = "sl-1234" #ldap服务器密码
ldapUsers = []

#获取用户dn
def getDN(username,total=False,retry=100):
    while retry > 0:
        try:
            l = ldap.initialize(ldappath)
            l.protocol_version = ldap.VERSION3
            l.simple_bind(ldapuser,ldappass)
            searchScope  = ldap.SCOPE_SUBTREE
            retrieveAttributes = None
            searchFilter = "(sAMAccountName=%s)" % username
            
            if total:
                ldap_result = l.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)
                return ldap_result
            else:
                ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
                result_type, result_data = l.result(ldap_result_id,1)
                dn = result_data[0][0]
            return dn
        except Exception:
            pass
        retry -= 1
    return False

#登陆验证 
def ldapLogin(username,passwd):
    dn = getDN(username)
    if dn:
        my_ldap = ldap.initialize(ldappath)
        try:
            try:
                name = dn.split(",")[0].strip('CN=')
            except Exception:
                name = str(username)
            my_ldap.simple_bind_s(dn,passwd)
            msg = "登陆成功"
            login = True
        except ldap.INVALID_CREDENTIALS:
            msg = u"用户名或密码错误"
            login = False
        except Exception,e:
            msg = str(e)
            login = False
    else:
        msg = u"用户名或密码错误"
        login = False
    
    logger.info("%s %s" %(username,msg))
    return login,msg

#从ldap同步账号
def syncUser():
    dns = getDN(username="*", total=True,retry=100)
    for item in dns:
        try:
            nickname = item[0].split(',')[0].strip('CN=')
            email = item[1]['mail'][0]
            name = item[1]['sAMAccountName'][0]
            try:
                user = Users.objects.get(name=name)
                user.nickname = nickname
                user.email = email
            except Users.DoesNotExist:
                user = Users(name=name,email=email,nickname=nickname)
                user.save()
                msg = "new user %s found" % name
                print msg
                logger.info(msg)
        except Exception:
            pass

if __name__ == "__main__":
    syncUser()