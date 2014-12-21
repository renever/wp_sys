# coding: utf-8
__author__ = 'lotaku'


#todo web GUI / Client GUi
#todo 添加网盘的支付帐号
#todo 为盘资源设置4个数字删除密码http://www.uploadable.ch/account_features.php


#todo 判断是否在列表里，用字符串，不要用实例，除非，定义实例的比较方法

#todo 考虑各种情况下抓取失败的url怎么处理，删除？

#todo 图片做备份
#todo 为每一个大步 建立try机制？中止或重启，并发邮件通知操作者
#todo 新建一个表，统计每天以发布文章数量，以及最后一次的发布时间
#todo 图片的requests 也要try 超时
#todo 有些文章有 压缩和非压缩文件 混合在一起的下载链接
#todo 连接 下载地址时，如果VPN 断了 ，会抛出 异常： Max retries exceeded with url
#todo 把一个文件分4线程同时下载
#todo 删除已经上传好的文件
#文章发布日期
# t2 = datetime.strftime(datetime.now(),'%b %d %Y' )