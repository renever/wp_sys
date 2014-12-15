#-*- encoding:utf8 -*-
import requests
from pyquery import PyQuery as pq
url = 'http://bbs.gope.cn/member.php?mod=logging&action=login'
r_session = requests.session()
r = r_session.get(url)
h = pq(r.text)
localtion = 'http://bbs.gope.cn/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LL783&inajax=1'
action =  h('form[class="cl"]').attr('action')
formhash =  h('input[name="formhash"]').attr('value')

action_real = 'http://bbs.gope.cn/' + action + '&inajax=1'

data = {
'answer':'',
'formhash':formhash,
'loginfield':'username',
'password':'123qwe',
'questionid':'0',
'referer':'http://bbs.gope.cn/./',
'username':'lxl002',
}
result = r_session.post(action_real,data=data)
print result.text