# -*- coding:utf-8 -*-
import spynner

if __name__ == "__main__":
	browser = spynner.Browser()
	# 设置代理
	#browser.set_proxy('http://host:port')
	browser.show()
	try:
		browser.load(url='http://www.uploadable.ch/login.php', load_timeout=120, tries=1)
	except spynner.SpynnerTimeout:
		print 'Timeout.'
	else:
		# 输入搜索关键字
		browser.wk_fill('input[id="userName"]', 'lxl001')
		browser.wk_fill('input[id="userPassword"]', 'qQ2@wW')
		# 点击搜索按钮，并等待页面加载完毕
		browser.wk_click('a[id="loginFormSubmit"]')
		browser.load(url='http://www.uploadable.ch/file/4XBstq46gFbN/chrome.part1.rar', load_timeout=120, tries=1)
		# 获取页面的HTML
		print 'html'
		html = browser.html
		if html:
			print 'write'
			html = html.encode('utf-8')
			open('search_results.html', 'w').write(html)
	browser.close()