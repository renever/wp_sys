import requests

def login_to_uploadable():
    """
    login to web sit :http://www.uploadable.ch
    """

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

    return r