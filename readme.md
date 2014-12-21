

安装说明：

官网下载 编译安装 python2.7.6
python默认安装目录在/usr/local/lib/python2.7，可以通过 /usr/local/bin/python -V 查看版本号
sudo ln -s /usr/include/python2.7 /usr/bin/python

sudo easy_install virtualenv
sudo easy_install virtualenvwrapper

sudo apt-get install libmysqld-dev
sudo apt-get install libxml2-dev libxslt1-dev python-dev

依赖：
pip install -r requirements.pip


注意：
调试时可以：/etc/mysql/my.cnf) removing the line bind-address=127.0.0.1
实际使用时记得恢复原样