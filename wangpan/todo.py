# coding: utf-8
__author__ = 'lotaku'

#todo 抓取下载地址的时候，用request抓取文件名
#todo web GUI / Client GUi
#todo 添加网盘的支付帐号
#todo ftp 上传后程序会有返回值，直接做判断用
#todo 压缩解压任务，都以文章原来的发布时间排序(发布时间需要抓取）
#todo 为盘资源设置4个数字删除密码http://www.uploadable.ch/account_features.php
#todo 修改pre_downloaded_file 方法
#todo 抓取到的新上传的链接，如果文件大小不符合，则是上传了一半的。post删除它
#todo 判断是否在列表里，用字符串，不要用实例，除非，定义实例的比较方法
#todo 根据更新时间下载文章，过滤条件要修改
#todo 旧下载链接失效了，要做异常处理
#todo 考虑各种情况下抓取失败的url怎么处理，删除？
#todo 注意body字段
#文章发布日期
# t2 = datetime.strftime(datetime.now(),'%b %d %Y' )