#- * - conding:utf-8 - * -
from pyquery import PyQuery as pq
#d = pq('<p class="hello" id="hello">you know Python rocks</p>')
#p = d('p')
#print p
#p.prepend('check out <a href="http://reddit.com/r/python">reddit</a>')
#print p.html()

#a = pq('<html><body><div id="test"><a href="http://python.org">python</a> !</div></body></html>')
#print a('#test').html()
#p.prependTo(a('#test'))
#print a('#test').html()
#print p.html()
#p.insertAfter(a('#test'))
#print a('#test').html()
#print a
#print a
#a.remove('#test')
#d =pq('<p class="hello">Hi</p><p>Bye</p><div></div>')
#print d('p').eq(0).attr('class')
h = pq(url='http://filmav.com/')
p = h(':contains("post")')
#p = h('div#post-51114')
print p('h2').html()

