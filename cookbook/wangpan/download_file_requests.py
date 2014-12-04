import requests

data = {
	'userName': 'lxl001',
	'userPassword': 'qQ2@wW',
}
headers = {
	'Request URL': 'http://www.uploadable.ch/login.php',
	'Accept-Encoding': 'gzip,deflate,sdch',
	'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.',
	'Connection': 'keep-alive',
	'Host': 'www.uploadable.ch',
	'Referer': 'http://www.uploadable.ch/login.php',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
}
url = 'http://www.uploadable.ch/login.php'
r = requests.post(url=url, data=data, headers=headers)
cookies = {'set-cookie': r.headers['set-cookie']}
from contextlib import closing


def download_file(url, r):
	local_filename = url.split('/')[-1]
	print local_filename
	# NOTE the stream=True parameter
	# b = requests.get(url, cookies=r.cookies)
	# print b.url

	with closing(requests.get(url, stream=True, cookies=r.cookies,allow_redirects=True)) as a:
		print a.content

		if a.status_code == 200:
			print 'oK'
		i = 0
		with open(local_filename, 'wb') as f:
			# for chunk in a.iter_content(chunk_size=1024):
			for chunk in a.iter_content(1024):
				if chunk:  # filter out keep-alive new chunks
					f.write(chunk)
					f.flush()
					i += 1
					print i
	print "end"
	# return local_filename


file_url = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'
# file_url = 'http://www.uploadable.ch/file/mKeajkRYutGy/client.py'
# file_url = 'http://pdl.uploadable.ch/file/SwkwFPd7scRC/yJjjJPhBdYlJIVTFXbCBgG0K77t5yexeS1SMccAZUPpTkUjjVCx4Yf86FyYTYDsKhdKryZC_e4_h9Ezc-ZfP0RQroH5C4v3gAyHOaMr85vSTHxjZQY9g-XdCY6FlWSTR12fS_S96MNRKjicseawPW69Xfge3QYdlULaAPv6yc9Y./123.pdf'
# file_url = 'http://pdl.uploadable.ch/file/SwkwFPd7scRC/eYGO-AuspglJjLQA1p9UN8wLbM-eu_gj5nCPp_jUi91m9LKjIZuEGYwfIakuch473rpkcpxAn2knVG91MxrZ9BQroH5C4v3gAyHOaMr85vSTHxjZQY9g-XdCY6FlWSTRLmn_NaAiGK920tmqibp0BOFeP_WiilgOpLhXhoZGC9k./123.pdf'
print download_file(file_url, r)
