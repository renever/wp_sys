# -*- coding: utf-8 -*-
from ghost import Ghost
ghost = Ghost()
page, extra_resources = ghost.open("http://www.baidu.com/")
assert page.http_status==200 and u'百度' in ghost.content