#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ldap, logging

logger = logging.getLogger("info")

ldappath = "ldap://192.168.80.10"   #ldap服务器地址
baseDN = "ou=KeWenDangDang,dc=dangdang,dc=com"  #根目录
ldapuser = "adsmart@dangdang.com"   #ldap服务器用户名
ldappass = "sl-1234"    #ldap服务器密码
ldapUsers = []

# 获取用户dn
def getDN(username, total=False, retry=30):
    while retry > 0:
        try:
            l = ldap.initialize(ldappath)
            l.protocol_version = ldap.VERSION3
            l.simple_bind(ldapuser, ldappass)
            searchScope  = ldap.SCOPE_SUBTREE
            retrieveAttributes = None
            searchFilter = "(sAMAccountName=%s)" % username
            
            if total:
                ldap_result = l.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)
                return ldap_result
            else:
                ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
                result_type, result_data = l.result(ldap_result_id, 1)
                dn = result_data[0][0]
            return dn
        except Exception,e:
            print e
            pass
        retry -= 1
    return False

# 登录验证
def ldapLogin(username, passwd):
    dn = getDN(username)
    if dn and passwd:
        my_ldap = ldap.initialize(ldappath)
        try:
            my_ldap.simple_bind_s(dn, passwd)
            login = True
            msg = "登录成功"
        except ldap.INVALID_CREDENTIALS:
            login = False
            msg = "用户名或密码错误，请重新输入"
        except Exception, e:
            login = False
            msg = str(e)
    else:
        msg = "用户名或密码错误，请重新输入"
        login = False
    return login, msg