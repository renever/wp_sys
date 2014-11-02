#- * - conding:utf-8 - * -
import requests
from pyquery import PyQuery as pq

h = requests.get(url='http://www.iplaysoft.com')
#print h.headers['content-type']
#print h.encoding
#print h.json()
a = pq(h.text)
# print a('div').find('.entry-title').eq(1).find('a').html()
# data = a('div').find('.entry-title')
data = a('h2.entry-title')
for d in data:
    # print dir(d)
    print pq(d)('a').attr('href')
