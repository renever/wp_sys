#-*- encoding:utf8 -*-
from articles import h16_30 as new_articles
import os
from post_to_6park import PostTo6park
for id in range(16,31):
	post_id = 'h'+ str(id)
	post_dict = getattr(new_articles,post_id)
	title_6park =  post_dict.get('title_6park').decode('utf-8')
	cover_img = post_dict.get('cover_img')
	screenshots = post_dict.get('screenshots')
	uploaded_net_links = post_dict.get('uploaded_net_links')
	rapidgator_links = post_dict.get('rapidgator_links')


	uploaded_net_links = "</br>".join(uploaded_net_links)
	rapidgator_links = "</br>".join(rapidgator_links)
	body = u'''{title_6park}</br>
<img src="{cover_img}"></br></br></br>
Download links</br></br>
{uploaded_net_links}</br></br>
{rapidgator_links}</br></br>
'''.format(title_6park=title_6park,
			   cover_img=cover_img,
			   # screenshots=screenshots,
			   uploaded_net_links=uploaded_net_links,
			   rapidgator_links=rapidgator_links,
			   )
	file_path = os.path.dirname(os.path.abspath(__file__)) + '/articles_6park/' + post_id
	with open(file_path,'w') as f:
		f.write(body.encode('utf-8'))
		f.flush()

	#todo 如果以为文件测试好规范后，改成True 发布跟帖，主贴手动发布
	#todo !!! IP 被屏蔽了，多次尝试登录。应该是防爬虫
	# # if True:
	# if post_id == 'h2':
	# 	post_to_6park = PostTo6park()
	# 	post_to_6park.url = 'http://www.cool18.com/bbs5/index.php?app=forum&act=dopost'
	# 	post_to_6park.data['rootid'] = '13292053'
	# 	post_to_6park.data['uptid'] = '13292053'
	# 	post_to_6park.run()
	# 	print '%s was posted to 6park' % post_id