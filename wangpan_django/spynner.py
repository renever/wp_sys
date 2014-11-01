# -*- encoding: utf-8 -*-
import spynner
import sys


if __name__ == "__main__":
	browser = spynner.Browser()

	#注释以下语句就是不打开窗口了
	browser.show()
	try:
		browser.load(url='http://www.lpfrx.com', load_timeout=120, tries=1)
	except spynner.SpynnerTimeout:
		print 'Timeout.'
	else:

		browser.wk_fill('input[id="s"]', 'delphi')
		browser.wait(3)

		#用javascript提交结果
		browser.runjs("document.forms[0].submit();")

		#另一种点击方式
		#browser.wk_click('a[href]',wait_load=True, timeout=8)
		browser.wait(3)

		#// 以下是获取超链接的元素，在第6个链接点击
		bb = browser.webframe.findAllElements('a')
		print len(bb)
		print sys.getdefaultencoding()

		anchor = bb[6]
		try:
			browser.wk_click_element_link(anchor, timeout=5)
		except spynner.SpynnerTimeout:
			print "timeou 5"

		browser.wait(5)
		html = browser.html
		if html:
			html = html.encode('utf-8')
			open('lpfrx.txt', 'w').write(html)
	browser.close()