# -*- coding: utf-8 -* -
import requests

def login_douban(username, passwd):
    post_data={'source':'index_nav','form_email':username,'form_password':passwd}
    request_headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0"}
    response=requests.post("http://www.douban.com/accounts/login", data=post_data,headers=request_headers)
    if u"豆瓣正在发生" in response.text:
        print response.text
        #return  response
        print "Login successful"
    else:
        print response.text
        print "Login failed"
        #return  False

login_douban('317399510@qq.com', 'dbF@ang11408')
